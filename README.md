# EmoGuard 认知照顾情绪监测系统

基于 Django + Django-Ninja 的情绪健康监测平台后端，为微信小程序提供 API 服务。

> **项目状态：稳定运维期** — 功能开发已完毕，不再新增特性，仅做必要维护。

## 功能模块

| 模块 | 说明 |
|------|------|
| 用户管理 | 微信 OpenID 登录 / 管理员账号登录，JWT 双令牌认证 |
| 情绪日记 | 用户主观情绪记录、日统计、趋势分析 |
| EMA 日常追踪 | 每日早晚情绪自评（抑郁/焦虑/精力/睡眠），服务端判定时段 |
| 认知评估 | 一次性提交 6 项量表（SCD/MMSE/MoCA/GAD-7/PHQ-9/ADL） |
| 量表系统 | 插件化量表架构（Python 定义类，registry 自动发现），已实现 GAD-7 |
| 健康报告 | 风险评级、趋势分析、专业建议 |
| 文章资讯 | 内容管理，草稿/发布状态 |
| 微信通知 | 订阅配额管理，每日早晚提醒推送（Celery Beat 定时任务） |
| 用户反馈 | 1-5 星评分反馈收集 |

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| Web 框架 | Django 5.2 + Django-Ninja Extra |
| 数据库 | PostgreSQL 15（生产）/ SQLite（本地开发） |
| 缓存/消息队列 | Redis 7 |
| 任务队列 | Celery 5.5 + django-celery-beat |
| WSGI | Gunicorn（单 worker） |
| 包管理 | uv（lockfile 锁定依赖） |
| 容器化 | Docker Compose（单机部署） |

## 架构

```
微信小程序 ──► Nginx (宿主机) ──► Gunicorn:8000 (Django)
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                    PostgreSQL:5432  Redis:6379   Celery Worker + Beat
```

- 后端、Celery Worker、PostgreSQL、Redis 均容器化运行
- Celery Beat 内嵌于 Worker（`-B` 参数），节省 ~133MB 内存
- 生产域名: `cg.aoxintech.com`

## 部署

### 环境变量

参考 `.env.example`，生产环境需要配置：

| 变量 | 说明 |
|------|------|
| `SECRET_KEY` | Django 密钥 |
| `JWT_SIGNING_KEY` | JWT 签名密钥（与 `SECRET_KEY` 解耦，独立管理；生产缺失即启动失败） |
| `POSTGRES_PASSWORD` | 数据库密码（已固化进数据卷，迁移/修改需同步 DB） |
| `REDIS_PASSWORD` | Redis 密码 |
| `DJANGO_SUPERUSER_USERNAME` / `_EMAIL` / `_PASSWORD` | 管理员账号 |
| `WECHAT_MINI_PROGRAM_APP_ID` / `_APP_SECRET` | 微信小程序凭证 |
| `WECHAT_SUBSCRIPTION_TEMPLATES` | 微信订阅消息模板 ID |

> **密钥管理约定**：运行时密钥由服务器 `/opt/emoguard/.env` 手工维护，CI/CD **不再生成或覆盖**该文件。
> 新增/轮换运行时密钥请编辑服务器 `/opt/emoguard/.env`，然后执行
> `ssh yecaoyun 'cd /opt/emoguard && docker compose -p emoguard -f docker-compose.yml --env-file .env up -d'`。
> GitHub Secrets 仅保留部署必须项（`SERVER_SSH_KEY` / `SERVER_HOST` / `SERVER_USER` 及自动注入的 `GITHUB_TOKEN`）。
> `/opt/emoguard/.env` 须离线加密备份（密码管理器 / sops），**严禁提交进 git**。

### 部署（CI/CD）

发布走 GitHub Actions 手动触发（`.github/workflows/deploy.yml`，`workflow_dispatch` → **Run workflow**）：无 push/PR 自动触发，`environment: dev` 无需人工审批。单次运行会：

1. 先检查部署输入文件和备份/恢复脚本语法，再构建镜像并推送 GHCR，tag 为提交短哈希（`<sha8>`）与 `latest`；
2. 将 `docker-compose.yml` 中的 `__IMAGE__` 渲染成本次镜像后上传至服务器 `/opt/emoguard/docker-compose.yml`；同一处把 `pre-deploy-backup.sh` / `db-restore.sh` 上传到 `/opt/emoguard/`（两个脚本按**本次工作流的提交**取，不随被部署提交回退）；
3. 校验 `/opt/emoguard/.env` 必需键**存在且非空**；
4. 确认命名数据卷存在；再调**宿主备份层** `cd /opt/server-ops && /usr/bin/python3 backup/cli.py run emoguard-db --kind pre-deploy --notify` 做部署前全库备份（CLI 按 `datasets.toml` 跑 `pg_dump`、代记账本、按 `dir`+`glob` 认产物并跑声明的 `verify`；宿主备份层缺失或备份失败都**立即失败、绝不静默跳过**），成功后才拉取镜像并执行 `docker compose up -d --remove-orphans`（不 `down`）；
5. 在容器内探测 `/health/`（最多 20 次、间隔 5 秒）；**`up` 失败或健康检查失败都会自动回滚到上一镜像 tag**；成功后把 tag 写入 `last_successful_version.txt`。

服务器目录布局：

| 路径 | 用途 |
|------|------|
| `/opt/emoguard/docker-compose.yml` | CI 渲染后上传，**勿手改**（下次部署覆盖） |
| `/opt/emoguard/.env` | 运行时密钥，手工维护，CI 不读不写 |
| `/opt/emoguard/last_successful_version.txt` | 最近一次成功部署的镜像 tag |
| `/opt/emoguard/docker-compose.rollback.yml` | 回滚时生成的临时编排，可删 |
| `/opt/emoguard/{pre-deploy-backup.sh,db-restore.sh}` | 备份/恢复入口；CI 按**本次工作流的提交**上传（不随被部署提交漂移） |
| `/var/www/emoguard/{media,staticfiles,logs}` | 绑定挂载；宿主机 nginx 直接读 `static/`、`media/` |
| `宿主机.conf` | 宿主机 nginx vhost（TLS + 静态/媒体 + 路由白名单）；改后 `nginx -t && systemctl reload nginx` |

全库备份由 `scripts/pre-deploy-backup.sh` 产出，入口统一到**宿主备份层** `/opt/server-ops`
（`backup/cli.py` + `backup/datasets.toml`，数据集名 `emoguard-db`），产物为
`/opt/emoguard/backups/pre-deploy-YYYYmmdd-HHMMSS.sql.gz`，最新路径写入 `.last-pre-deploy`。
检查 `pg_dump` 退出码、gzip 完整性及 dump 头尾标记；失败即失败（周期运行记 `fail`，CI 部署中止）。
写操作共用文件锁，同秒运行不覆盖旧文件。保留最近 30 份（宿主 `datasets.toml` 的 `KEEP_N=30`；
脚本内默认 10 只在脱离宿主层直跑时生效）、6 小时内文件及 `.pre-deploy-keep` 指定锚点；
清单缺失／不可读或参数非法时拒绝裁剪，但不影响已成功的备份。
不需要锚点时，管理员可明确保留空清单。脚本不再自动补空清单。
只匹配 `pre-deploy-*.sql`／`.sql.gz`，不清理其他备份。

该备份是 gzip 包装的 SQL，不是 `pg_restore` 使用的 custom dump；需要解压后用相同
PostgreSQL 大版本的 `psql` 导入准备好的干净目标库，并核对角色、扩展和应用版本。
这些是格式与版本前提，不是恢复成功证明；镜像回滚不会自动回滚数据库。

接入宿主备份层之后的四条腿：

- **周期全库备份**：宿主每日 **04:20** 由 `backup/cli.py run emoguard-db` 调度（命令与 `KEEP_N`
  都写在 `datasets.toml` 里；cron 只调 CLI，项目侧已不再有独立 cron 行）；
- **发布前快照**：CI 部署前调 `cli.py run emoguard-db --kind pre-deploy --notify`，与周期备份同目录、
  共用保留窗；`--notify` 的失败告警走宿主唯一通知入口（受静音开关约束）；
- **异地冷副本**：宿主备份落盘后**推送**到树莓派（单向只增：接收端拒绝同名覆盖、无删除接口），
  每项目只保留最新 1 份并做格式校验；树莓派侧不提供恢复入口，紧急时手工拷回宿主再恢复；
- **事件账本**：`/opt/server-ops/backup/events.jsonl`（`cli.py log` / `status` / `audit` 可查；
  `audit` 每日 09:15 在宿主跑，仅高危推送）。

媒体文件（`/var/www/emoguard/media`）与 Redis 不在 SQL 中：媒体需另行处理，Redis 视为可丢弃缓存。

### 恢复

恢复入口是 `scripts/db-restore.sh`，随部署上传为 `/opt/emoguard/db-restore.sh`。**默认不写库**：
先做 gzip/头部校验并打印将被覆盖的对象数，加了 `--yes` 才动手。

```bash
ssh yecaoyun
ls -t /opt/emoguard/backups/pre-deploy-*.sql.gz | head    # 选一份
# 只打印摘要（不写库，不必 --yes）
bash /opt/emoguard/db-restore.sh /opt/emoguard/backups/pre-deploy-20260921-023856.sql.gz
# 真的恢复
bash /opt/emoguard/db-restore.sh /opt/emoguard/backups/pre-deploy-20260921-023856.sql.gz --yes
```

`--yes` 时的顺序与护栏（任一步失败即中止，不会"做一半还接着往下走"）：

1. **急救快照**：先调同目录的 `pre-deploy-backup.sh backup`，把当前库 dump 成
   `/opt/emoguard/backups/pre-deploy-<时间戳>.sql.gz`（路径同时写入 `.last-pre-deploy`，照常入账本、
   进保留窗与异地副本）；快照失败即中止，**不动库**；
2. **清空 + 导入**：清掉 `public` 下现有表与残留序列后，`gunzip -c | psql -v ON_ERROR_STOP=1` 导入，
   任一语句失败即中止 —— dump 是 plain 且不带 `--clean`，所以必须先清空；
3. **对齐 schema**：在 `emoguard-backend` 内跑 `uv run python manage.py migrate --noinput`
   （dump 里的 `django_migrations` 是备份时刻的状态，备份早于代码时需要这条对齐）；
4. 退出码：`0` 成功 • `1` 参数/环境错（含急救快照失败）• `2` 备份文件不存在或损坏 • `3` 写库失败 •
   `4` migrate 失败。

恢复会**覆盖当前数据且不可逆**，建议在业务低峰执行；摘要模式可以先不写库看一眼代价。
回退本次恢复直接用脚本打印的急救快照路径再跑一次即可。

手工回滚（CI 回滚未生效，或需指定更早版本时）：

```bash
ssh yecaoyun
cd /opt/emoguard
TAG=$(cat last_successful_version.txt)   # 也可填任意历史 tag（见 docker images）
sed -E "s|image: .*emoguard-backend.*|image: ghcr.io/fire-disposal/emoguard_project/emoguard-backend:${TAG}|" \
  docker-compose.yml > docker-compose.rollback.yml
docker compose -p emoguard -f docker-compose.rollback.yml --env-file .env up -d --remove-orphans
```

> **数据卷红线**：`emoguard_pg_data` / `emoguard_redis_data` 在编排中声明为 `external: true`，compose 只引用、不创建也不删除。
> **严禁 `docker compose down -v` / `docker volume rm`**——那会清空全部业务数据。
> `POSTGRES_PASSWORD` 已固化进 `emoguard_pg_data`，改值会导致数据库不可访问；新宿主机首次部署前需先建这两个卷（CI 前置检查会自动创建）。

### 本地开发

`docker-compose.override.yml` 仅供本地：将 backend / celery-worker 改为 `build: .` 并标记为 `emoguard-backend:local`。
生产编排中的 `image: __IMAGE__` 是 CI 渲染占位符，不是合法镜像名——**在未渲染的编排上直接 `docker compose build` 会失败**，本地务必让 override 生效（同目录 `docker compose` 命令默认即生效），并先复制 `.env.example` 为 `.env` 填值。
本地不启 nginx（override 中该服务已停用），TLS 由宿主机 nginx 承担。

### 健康检查

```bash
curl http://localhost:8000/health/
```

返回数据库和缓存连接状态（不健康时返回 503）。

## API 文档

启动后访问 `http://localhost:8000/api/docs` 查看 Swagger 交互式文档。

### 主要端点

| 端点 | 说明 |
|------|------|
| `POST /api/users/wechat/login` | 微信小程序登录 |
| `POST /api/users/admin/login` | 管理员登录 |
| `POST /api/token/refresh/` | 刷新 JWT（旋转 + 旧令牌加入黑名单；限流 10次/分钟） |
| `GET /api/emotiontracker/trend` | 30 天情绪趋势 |
| `POST /api/cognitive/submit` | 提交认知评估 |
| `GET /api/scales/{code}/questions` | 获取量表题目 |

## 目录结构

```
emoguard_project/
├── apps/                  # Django 应用
│   ├── users/             # 用户与认证
│   ├── articles/          # 文章资讯
│   ├── journals/          # 情绪日记
│   ├── emotiontracker/    # EMA 日常追踪
│   ├── scales/            # 量表系统
│   ├── cognitive_flow/    # 认知评估
│   ├── reports/           # 健康报告
│   ├── notice/            # 微信通知
│   └── feedback/          # 用户反馈
├── config/                # Django 配置
├── miniprogram/           # 微信小程序前端
├── doc/                   # 文档
├── docker-compose.yml     # 生产部署编排
├── Dockerfile             # 应用镜像
└── pyproject.toml         # 依赖声明
```

## 维护说明

- 依赖更新：修改 `pyproject.toml` 后运行 `uv lock`，重新构建镜像
- 定时任务：`setup_periodic_tasks` 管理命令（容器启动自动执行）
- 量表配置：Python 定义类位于 `apps/scales/definitions/`，由 registry 在运行时自动发现
- JWT 有效期：access 24 小时 / refresh 30 天（启用轮换 + 黑名单，支持吊销）
- Python 版本要求：≥ 3.13
- 管理员联系邮箱：3295829485@qq.com
