#!/usr/bin/env bash
# ==============================================================
#  db-restore.sh —— emoguard 数据库恢复（plain SQL + gzip）
#
#  用法:
#    ./db-restore.sh <备份文件路径>            # 只校验并打印摘要，不写库
#    ./db-restore.sh <备份文件路径> --yes      # 实际恢复（写库）
#
#  为什么单独成脚本：备份只有能恢复才算备份。宿主备份层（backup/cli.py run）只负责
#  产出与记账，回滚路径此前完全缺失 —— 出事时只能靠人回忆 docker exec 该怎么敲。
#
#  安全机制（顺序即防线，上一步不成功就绝不进入下一步）:
#    1. 没有 --yes 一律拒绝写库，只打印将被覆盖的对象摘要（账本记 refused）
#    2. 写库前先做急救快照：调用同目录的 pre-deploy-backup.sh backup
#       （产物落 $BACKUP_DIR/pre-deploy-<时间戳>.sql.gz：同样入账本、进保留窗与异地副本）
#    3. gzip -t + dump 头部标记校验备份完整性
#    4. 清空 public 现有对象后导入；psql -v ON_ERROR_STOP=1，任一语句失败即中止
#    5. 导入后在 backend 容器内跑 manage.py migrate --noinput，对齐 dump 之后的 schema
#
#  站点默认值（与 pre-deploy-backup.sh 的站点区一致，可用同名环境变量覆盖）:
#    BACKUP_DIR=/opt/emoguard/backups  PG_CONTAINER=emoguard-db
#    PG_USER=emoguard  PG_DB=emoguard  APP_CONTAINER=emoguard-backend
#
#  退出码:
#    0 = 成功（含未带 --yes 的摘要模式）
#    1 = 参数/环境错误（含急救快照失败 —— 没有退路就不动库）
#    2 = 备份文件不存在或损坏（gzip/头部标记）
#    3 = 写库失败（清空现有对象或导入中断，或导入后目标库仍是空的）
#    4 = schema 对齐失败（manage.py migrate 非零）
# ==============================================================
set -euo pipefail

# ── 备份事件账本接线（宿主 /opt/server-ops/backup/lib.sh）────────────────────
# 库缺失时退化为空实现：脚本仍可独立运行（fail-open，见 server-ops docs/backup-design.md §10）
BK_LIB="${BK_LIB:-/opt/server-ops/backup/lib.sh}"
if [ -r "$BK_LIB" ]; then
  # shellcheck source=/dev/null
  . "$BK_LIB"
else
  bk_begin() { :; }; bk_artifact() { :; }; bk_context() { :; }; bk_note() { :; }
  bk_restore_begin() { :; }; bk_restore_end() { :; }; bk_refused() { :; }
fi

# ── 站点默认值（本文件唯一的仓库差异区）──
BACKUP_DIR="${BACKUP_DIR:-/opt/emoguard/backups}"
PG_CONTAINER="${PG_CONTAINER:-emoguard-db}"
PG_USER="${PG_USER:-emoguard}"
PG_DB="${PG_DB:-emoguard}"
APP_CONTAINER="${APP_CONTAINER:-emoguard-backend}"
DATASET="${DATASET:-emoguard-db}"   # 事件账本数据集名

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 两种布局下"同目录"都成立：仓内 scripts/{db-restore,pre-deploy-backup}.sh、
# 宿主 flat 布局 /opt/emoguard/{db-restore,pre-deploy-backup}.sh。
PRE_DEPLOY_BACKUP="${PRE_DEPLOY_BACKUP:-$SCRIPT_DIR/pre-deploy-backup.sh}"
STATE_FILE="$BACKUP_DIR/.last-pre-deploy"

BACKUP_FILE="${1:-}"
AUTO_YES="${2:-}"

log() { printf '%s %s\n' "$(date '+%F %T')" "$*" >&2; }

usage() {
  cat >&2 <<'USAGE'
用法: db-restore.sh <备份文件路径> [--yes]
  <备份文件路径>  pre-deploy-*.sql.gz（pg_dump plain + gzip）
  不带 --yes      只校验并打印摘要，不写库
  带   --yes      真的恢复（会清空目标库 public 下的现有对象）
USAGE
}

running() { # running <container> → 0/1
  [ "$(docker inspect -f '{{.State.Running}}' "$1" 2>/dev/null)" = "true" ]
}

# ── 参数校验（退出码 1）──
if [ "$#" -gt 2 ]; then
  echo "[ERR] 参数过多：$*" >&2
  usage
  exit 1
fi
if [ -z "$BACKUP_FILE" ]; then
  echo "[ERR] 缺少备份文件路径" >&2
  usage
  exit 1
fi
case "$BACKUP_FILE" in
  -h | --help) usage; exit 0 ;;
  -*) echo "[ERR] 未知参数：$BACKUP_FILE（第一个参数必须是备份文件路径）" >&2; usage; exit 1 ;;
esac
case "$AUTO_YES" in
  '' | --yes) ;;
  *) echo "[ERR] 未知参数：$AUTO_YES（只支持 --yes）" >&2; usage; exit 1 ;;
esac

# ── 环境校验（退出码 1）──
command -v docker >/dev/null 2>&1 || { echo "[ERR] 找不到 docker" >&2; exit 1; }
if [ ! -r "$PRE_DEPLOY_BACKUP" ]; then
  echo "[ERR] 找不到同目录的 pre-deploy-backup.sh：$PRE_DEPLOY_BACKUP" >&2
  echo "      急救快照是本脚本的前置条件（没有退路就不动库）" >&2
  exit 1
fi
running "$PG_CONTAINER" || { echo "[ERR] 数据库容器未运行：$PG_CONTAINER" >&2; exit 1; }

# ── 备份文件校验（退出码 2）──
if [ ! -f "$BACKUP_FILE" ]; then
  echo "[ERR] 备份文件不存在: $BACKUP_FILE" >&2
  exit 2
fi
if [ ! -r "$BACKUP_FILE" ]; then
  echo "[ERR] 备份文件不可读: $BACKUP_FILE" >&2
  exit 2
fi
echo "[..] 校验备份文件完整性 ..."
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "[ERR] 备份文件损坏（gzip 校验失败）: $BACKUP_FILE" >&2
  exit 2
fi
# 头部标记：排除"能解压但不是 pg_dump 明文"的文件（与 pre-deploy-backup.sh 落盘前的校验同源）
HDR="$(gzip -dc "$BACKUP_FILE" 2>/dev/null | head -c 4000 || true)"
case "$HDR" in
  *"PostgreSQL database dump"*) ;;
  *)
    echo "[ERR] 不是 pg_dump 明文 dump（缺少头部标记）: $BACKUP_FILE" >&2
    exit 2
    ;;
esac
SIZE="$(du -h "$BACKUP_FILE" | cut -f1)"
echo "[OK] 文件完整性校验通过 (${SIZE})"

# 当前库内对象数：既是摘要依据，也是恢复后的对照基线
if ! TABLES_BEFORE="$(docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB" -tAc \
  "SELECT count(*) FROM pg_tables WHERE schemaname = 'public'")"; then
  echo "[ERR] 无法查询数据库（容器 $PG_CONTAINER / 库 $PG_DB）" >&2
  exit 1
fi
TABLES_BEFORE="${TABLES_BEFORE//[[:space:]]/}"

echo ""
echo "  ⚠  即将恢复 emoguard 数据库"
echo "     源文件   : ${BACKUP_FILE}  (${SIZE})"
echo "     目标     : 容器 ${PG_CONTAINER} 的 ${PG_USER}@${PG_DB}（public 现有 ${TABLES_BEFORE} 张表将被清空）"
echo "     急救快照 : ${BACKUP_DIR}/pre-deploy-<时间戳>.sql.gz（导入前自动创建）"
echo "     schema   : 导入后在 ${APP_CONTAINER} 内跑 manage.py migrate --noinput"
echo ""

# ── 守卫：无 --yes 只打印摘要（账本记 refused，一等结果）──
if [ "$AUTO_YES" != "--yes" ]; then
  echo "[..] 未指定 --yes：只打印摘要，不写库"
  bk_restore_begin "$DATASET" restore "$(id -un)" "$BACKUP_FILE"
  bk_refused "未带 --yes：只打印摘要，未写库"
  exit 0
fi

running "$APP_CONTAINER" || {
  echo "[ERR] 应用容器未运行：$APP_CONTAINER（导入后要跑 migrate 对齐 schema）" >&2
  exit 1
}

# 参数/环境/完整性校验都过了，真正开始恢复前记 attempt
# （本脚本不自带 EXIT trap，退出时由 bk_restore_begin 挂的 trap 记 ok/fail/refused）
bk_restore_begin "$DATASET" restore "$(id -un)" "$BACKUP_FILE"

# ── 第 1 步：急救快照 ──
# 没有它，"恢复错了"就无路可退 —— 所以它失败时绝不继续（宿主同款脚本自带 gzip/头尾校验）。
echo "[..] 创建急救快照（恢复前的数据）..."
if ! bash "$PRE_DEPLOY_BACKUP" backup; then
  echo "[ERR] 急救快照失败 —— 未写库（先把备份修好再恢复）" >&2
  exit 1
fi
EMERGENCY_FILE="$(cat "$STATE_FILE" 2>/dev/null || true)"
if [ -n "$EMERGENCY_FILE" ] && [ -s "$EMERGENCY_FILE" ]; then
  echo "[OK] 急救快照: ${EMERGENCY_FILE} ($(du -h "$EMERGENCY_FILE" | cut -f1))"
else
  echo "[WARN] 备份脚本报告成功，但 ${STATE_FILE} 未指向可用文件 —— 快照请到 ${BACKUP_DIR} 人工确认" >&2
  EMERGENCY_FILE="${BACKUP_DIR}/（最新一份 pre-deploy-*.sql.gz）"
fi

# ── 第 2 步：清空现有对象 + 导入 ──
# dump 是 pg_dump plain 且不带 --clean：直接导入会满屏 "already exists" 并在
# ON_ERROR_STOP=1 下立刻中止 —— 必须先清空 public 下的现有对象。
echo "[..] 清空 public 现有对象（表及其随附的序列/索引/约束）..."
if ! docker exec -i "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 -q <<'SQL'
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
    EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
  END LOOP;
  -- 表已 DROP ... CASCADE（自有序列随之消失）；这里兜底清掉非 owned 的残留序列，
  -- 否则 dump 里的 CREATE SEQUENCE 会因 "already exists" 卡住导入。
  FOR r IN (SELECT sequencename FROM pg_sequences WHERE schemaname = 'public') LOOP
    EXECUTE 'DROP SEQUENCE IF EXISTS public.' || quote_ident(r.sequencename) || ' CASCADE';
  END LOOP;
END $$;
SQL
then
  echo "[ERR] 清空现有对象失败 —— 已中止，未导入任何数据" >&2
  exit 3
fi

echo "[..] 正在导入 ${BACKUP_FILE} ..."
if ! gunzip -c "$BACKUP_FILE" | docker exec -i "$PG_CONTAINER" \
  psql -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1; then
  echo "[ERR] 数据导入失败（psql 非零退出）" >&2
  echo "[..] 如需回退本次恢复: $0 ${EMERGENCY_FILE} --yes" >&2
  exit 3
fi
echo "[OK] 数据导入完成"

# ── 第 3 步：schema 对齐 ──
# dump 里的 django_migrations 是备份时刻的状态；备份早于当前代码时，模型与库会错位。
# 与 docker-entrypoint.sh 的 backend 初始化同一条命令（uv run，WORKDIR=/app）。
echo "[..] 在 ${APP_CONTAINER} 内跑 migrate --noinput ..."
if ! docker exec "$APP_CONTAINER" uv run python manage.py migrate --noinput; then
  echo "[ERR] schema 对齐失败（manage.py migrate 非零）—— 数据已导入，请人工检查" >&2
  exit 4
fi

# ── 第 4 步：结果核对 ──
TABLES_AFTER="$(docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB" -tAc \
  "SELECT count(*) FROM pg_tables WHERE schemaname = 'public'")"
TABLES_AFTER="${TABLES_AFTER//[[:space:]]/}"
echo "[OK] public 表数: ${TABLES_BEFORE} → ${TABLES_AFTER}"
if [[ ! $TABLES_AFTER =~ ^[0-9]+$ ]] || (( TABLES_AFTER == 0 )); then
  echo "[ERR] 导入报成功但目标库 public 下没有表 —— 视为恢复失败" >&2
  exit 3
fi

bk_note "public 表数 ${TABLES_BEFORE} → ${TABLES_AFTER}；migrate --noinput 已跑；急救快照 ${EMERGENCY_FILE}"
echo ""
echo "[OK] 恢复完成"
echo "     如发现问题, 可回退到恢复前的数据: $0 ${EMERGENCY_FILE} --yes"
