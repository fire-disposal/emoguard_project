# 项目状态

**当前阶段：稳定运维期**

项目功能开发已完毕，无新增功能计划。当前仅进行必要的安全更新和 bug 修复。

## 运维事项

- 定期更新 Python 依赖（安全补丁）
- 监控磁盘空间（PostgreSQL / 日志 / media）
- 关注微信小程序 API 兼容性变更
- JWT 签名密钥轮换（如需）

## 部署与回滚

- 发布：GitHub Actions 手动触发 **Build & Deploy Backend Stack**（无 push/PR 自动触发）
- 部署目录 `/opt/emoguard`：`.env`（手工维护的密钥）、`docker-compose.yml`（CI 渲染上传）、`last_successful_version.txt`（上次成功 tag）
- 回滚：CI 在 `compose up` 失败或健康检查失败时自动回退到上一 tag；手工步骤见 `README.md` 部署章节
- 数据卷 `emoguard_pg_data` / `emoguard_redis_data` 已声明 `external: true`：**严禁 `docker compose down -v` 或 `docker volume rm`**（会清空业务数据）；`POSTGRES_PASSWORD` 固化进卷，改值即导致数据库不可访问
- 备份：`/opt/emoguard/.env` 与 PostgreSQL 数据须离线加密备份（密码管理器 / sops），严禁进 git
