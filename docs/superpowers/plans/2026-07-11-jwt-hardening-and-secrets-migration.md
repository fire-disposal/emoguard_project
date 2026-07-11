# JWT 强化与密钥迁移 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复令牌刷新链路的客户端与后端缺陷,并把非部署必须的运行时密钥从 GitHub Secrets 迁回服务器手动管理的 `~/.env`。

**Architecture:** 后端(Django 5.2 + django-ninja-jwt)引入 `token_blacklist` 实现真轮换+可吊销、拆分独立签名密钥并 fail-fast、缩短 access 时长、令牌日志脱敏、限流/防重放迁 Redis;小程序修复熔断 dead-end;CI/CD 停止重写 `~/.env`,GitHub 仅保留部署必须密钥。

**Tech Stack:** Python 3.13 / uv / Django 5.2 / django-ninja-jwt / Celery / Redis / PostgreSQL / GitHub Actions / 微信小程序。

**关键决策(已确认):**
- access token 生命周期 → **24 小时**(消费级低安全系统的行业宽松值;refresh 保持 30 天并启用轮换,使刷新路径每日被行使从而缺陷即时暴露)。
- 现在引入 `token_blacklist`(真轮换 + 可吊销)。
- 拆出独立 `JWT_SIGNING_KEY`,**不轮换**现有值(存量令牌不失效)。
- 单一客户端刷新端点:`/api/token/refresh/`(带斜杠),行为=旋转+黑名单。

**执行顺序铁律:**
1. 阶段 1(后端)可独立部署,不影响存量令牌(不轮换密钥、access 变短仅对新签发生效)。
2. 阶段 2(小程序)需过微信审核发版;**必须在缩短 access 时长带来的高频刷新暴露给大量用户之前上线**。
3. 阶段 3(密钥迁移)**必须先改 `deploy.yml` 停写 `.env`,再删 GitHub Secrets**,否则空值会覆盖 `~/.env`。

---

## 阶段 0:测试基础设施

当前仓库无任何测试与测试框架。使用 Django 原生 test runner + 独立 sqlite 测试配置(零新增依赖)。

### Task 0.1: 新增测试专用 settings

**Files:**
- Create: `config/settings_test.py`

- [ ] **Step 1: 写测试配置**

```python
"""测试专用配置:内存 SQLite、同步 Celery、显式 JWT 签名密钥。
用法: uv run python manage.py test --settings=config.settings_test
"""
from config.settings import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

CELERY_TASK_ALWAYS_EAGER = True

# 显式提供签名密钥,规避阶段 1 引入的 fail-fast 校验
JWT_SIGNING_KEY = "test-only-signing-key-not-for-production"
NINJA_JWT = {**NINJA_JWT, "SIGNING_KEY": JWT_SIGNING_KEY}  # noqa: F405

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

- [ ] **Step 2: 验证测试运行器可启动**

Run: `uv run python manage.py test --settings=config.settings_test --help`
Expected: 显示 test 命令帮助,无导入错误。

- [ ] **Step 3: Commit**

```bash
git add config/settings_test.py
git commit -m "test: add sqlite-based test settings module"
```

---

## 阶段 1:后端 JWT 强化

### Task 1.1: 拆出独立 JWT_SIGNING_KEY 并 fail-fast

**Files:**
- Modify: `config/settings.py:208-223`
- Test: `config/tests/test_jwt_settings.py` (Create)

- [ ] **Step 1: 写失败测试**

```python
# config/tests/__init__.py 为空文件
# config/tests/test_jwt_settings.py
from django.test import SimpleTestCase
from django.conf import settings


class JwtSigningKeyTests(SimpleTestCase):
    def test_signing_key_is_decoupled_from_secret_key(self):
        self.assertIn("SIGNING_KEY", settings.NINJA_JWT)
        self.assertEqual(
            settings.NINJA_JWT["SIGNING_KEY"], settings.JWT_SIGNING_KEY
        )

    def test_signing_key_not_the_insecure_secret_fallback(self):
        self.assertNotIn(
            "django-insecure", settings.NINJA_JWT["SIGNING_KEY"]
        )
```

- [ ] **Step 2: 运行,确认失败**

Run: `uv run python manage.py test config.tests.test_jwt_settings --settings=config.settings_test -v2`
Expected: FAIL(`JWT_SIGNING_KEY` 尚不存在 / SIGNING_KEY 仍为 SECRET_KEY)。

- [ ] **Step 3: 实现拆分与 fail-fast**

将 `config/settings.py` 的 JWT 段替换为:

```python
# =============================================================================
# JWT 认证配置
# =============================================================================

# JWT 签名密钥与 Django SECRET_KEY 解耦。
# 生产(DEBUG=False)必须由环境变量提供,缺失即启动失败(fail-fast),
# 避免静默回落到不安全默认值导致全量令牌被错误签发。
JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY")
if not JWT_SIGNING_KEY:
    if DEBUG:
        JWT_SIGNING_KEY = SECRET_KEY
    else:
        raise RuntimeError(
            "JWT_SIGNING_KEY 未设置。生产环境必须通过环境变量提供该密钥。"
        )

NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('ninja_jwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'users.User',
}
```

> 说明:`JWT_SIGNING_KEY` 迁移期先沿用现有 `SECRET_KEY` 的值(见阶段 3),故存量令牌不失效。

- [ ] **Step 4: 运行,确认通过**

Run: `uv run python manage.py test config.tests.test_jwt_settings --settings=config.settings_test -v2`
Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add config/settings.py config/tests/__init__.py config/tests/test_jwt_settings.py
git commit -m "feat(jwt): decouple JWT_SIGNING_KEY from SECRET_KEY with prod fail-fast"
```

### Task 1.2: 启用 token_blacklist 应用

**Files:**
- Modify: `config/settings.py:54-82` (INSTALLED_APPS)

- [ ] **Step 1: 注册黑名单应用**

在 `INSTALLED_APPS` 的第三方框架段,`"ninja_jwt",` 之后新增一行:

```python
    "ninja_jwt.token_blacklist",
```

- [ ] **Step 2: 生成并检查迁移**

Run: `uv run python manage.py migrate --settings=config.settings_test`
Expected: 应用 `token_blacklist` 的迁移(创建 OutstandingToken / BlacklistedToken 表),无报错。

- [ ] **Step 3: Commit**

```bash
git add config/settings.py
git commit -m "feat(jwt): enable ninja_jwt token_blacklist app"
```

### Task 1.3: 刷新端点实现旋转+黑名单,统一契约

**Files:**
- Modify: `config/jwt_auth_adapter.py:29-44`
- Test: `apps/users/tests/test_token_refresh.py` (Create)

- [ ] **Step 1: 写失败测试**

```python
# apps/users/tests/__init__.py 为空文件
# apps/users/tests/test_token_refresh.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError
from config.jwt_auth_adapter import refresh_access_token

User = get_user_model()


class RefreshRotationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="openid_x", role="user")

    def test_refresh_returns_new_access_and_refresh(self):
        tokens = RefreshToken.for_user(self.user)
        result = refresh_access_token(str(tokens))
        self.assertIsNotNone(result)
        self.assertIn("access", result)
        self.assertIn("refresh", result)
        self.assertNotEqual(result["refresh"], str(tokens))

    def test_old_refresh_is_blacklisted_after_rotation(self):
        tokens = RefreshToken.for_user(self.user)
        old = str(tokens)
        refresh_access_token(old)
        # 旧 refresh 再次使用应因黑名单而失败
        second = refresh_access_token(old)
        self.assertIsNone(second)

    def test_invalid_token_returns_none(self):
        self.assertIsNone(refresh_access_token("not-a-token"))
```

- [ ] **Step 2: 运行,确认失败**

Run: `uv run python manage.py test apps.users.tests.test_token_refresh --settings=config.settings_test -v2`
Expected: FAIL(`test_old_refresh_is_blacklisted_after_rotation` 失败——当前实现不拉黑旧令牌)。

- [ ] **Step 3: 实现旋转+黑名单**

将 `config/jwt_auth_adapter.py` 的 `refresh_access_token` 替换为:

```python
def refresh_access_token(refresh_token_str):
    """使用刷新令牌换取新的访问令牌。

    启用 ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION 后:
    - 校验旧 refresh;
    - 签发新 access;
    - 将旧 refresh 加入黑名单并签发新的 refresh(真轮换)。
    失败返回 None(旧令牌被拉黑或过期/无效)。
    """
    try:
        refresh = RefreshToken(refresh_token_str)
        access = str(refresh.access_token)

        new_refresh = refresh
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        else:
            new_refresh = RefreshToken.for_user(
                User.objects.get(id=refresh["user_id"])
            )

        result = {"access": access, "refresh": str(new_refresh)}
        logger.info(
            "[JWT] 刷新成功: user_id=%s", refresh.get("user_id", "?")
        )
        return result
    except (TokenError, InvalidToken, User.DoesNotExist) as e:
        logger.warning("[JWT] 刷新失败: %s", str(e))
        return None
```

- [ ] **Step 4: 运行,确认通过**

Run: `uv run python manage.py test apps.users.tests.test_token_refresh --settings=config.settings_test -v2`
Expected: PASS(3 项)。

- [ ] **Step 5: Commit**

```bash
git add config/jwt_auth_adapter.py apps/users/tests/__init__.py apps/users/tests/test_token_refresh.py
git commit -m "feat(jwt): rotate and blacklist refresh tokens on refresh"
```

### Task 1.4: 令牌日志脱敏

**Files:**
- Modify: `config/jwt_auth_adapter.py:17-27,46-58`

- [ ] **Step 1: 脱敏 create_tokens_for_user**

将 `create_tokens_for_user` 中的 `logger.info(...)` 一行替换为:

```python
    logger.info("[JWT] 签发令牌: user_id=%s", user.id)
```

- [ ] **Step 2: 脱敏 get_user_from_token**

将 `get_user_from_token` 内两处打印完整 `token_str`/`user_id` 的 `logger.info` 调用替换为不含令牌明文的形式:

```python
def get_user_from_token(token_str):
    """从令牌字符串中获取用户"""
    try:
        refresh = RefreshToken(token_str)
        user_id = refresh['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist) as e:
        logger.warning("[JWT] 令牌解析失败: %s", str(e))
        return None
```

- [ ] **Step 3: 全文件确认无令牌明文日志**

Run: `uv run python -c "import re,sys; s=open('config/jwt_auth_adapter.py',encoding='utf-8').read(); sys.exit(1 if re.search(r'str\(refresh', s) and 'logger' in s and 'access=' in s else 0)"`
Expected: 退出码 0(不再打印 access/refresh 明文)。人工复核该文件所有 `logger.*` 行均不含 token 变量。

- [ ] **Step 4: 回归测试**

Run: `uv run python manage.py test apps.users config --settings=config.settings_test -v2`
Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add config/jwt_auth_adapter.py
git commit -m "fix(jwt): redact token secrets from logs, lower refresh-fail to warning"
```

### Task 1.5: 限流与防重放迁移到 Redis,清理死代码

**Files:**
- Modify: `config/settings.py:261-282` (CACHES)
- Modify: `apps/users/views.py:145-168` (wechat_login 接入防重放)
- Test: `apps/users/tests/test_wechat_replay.py` (Create)

- [ ] **Step 1: 写失败测试(防重放)**

```python
# apps/users/tests/test_wechat_replay.py
from django.test import TestCase
from django.core.cache import cache
from apps.users.wechat_auth import WeChatAuthService


class WeChatReplayTests(TestCase):
    def setUp(self):
        cache.clear()
        self.svc = WeChatAuthService()

    def test_same_code_rejected_on_second_use(self):
        code = "a" * 32
        self.svc.validate_wechat_code(code)
        with self.assertRaises(Exception):
            self.svc.validate_wechat_code(code)
```

- [ ] **Step 2: 运行,确认通过(此测试验证既有方法本身正确)**

Run: `uv run python manage.py test apps.users.tests.test_wechat_replay --settings=config.settings_test -v2`
Expected: PASS(`validate_wechat_code` 方法逻辑本就正确;此测试锁定行为,便于下一步接入视图时不回归)。

- [ ] **Step 3: 在 wechat_login 中接入防重放**

在 `apps/users/views.py` 的 `wechat_login` 内,`len(data.code) != 32` 校验之后、`wechat_service.get_access_token(data.code)` 之前,插入:

```python
    try:
        wechat_service.validate_wechat_code(data.code)
    except Exception:
        raise HttpError(400, "微信登录凭证已使用或无效")
```

- [ ] **Step 4: CACHES 默认后端切换为 Redis**

将 `config/settings.py` 的 `CACHES` 替换为:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get(
            'CACHE_URL',
            os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1'),
        ),
    },
    'database': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
        'OPTIONS': {'MAX_ENTRIES': 10000},
    },
}
```

> 说明:限流(`rate_limit.py`)与防重放(`validate_wechat_code`)均走 `default` 缓存;改 Redis 后跨进程(gunicorn/celery)与跨重启一致。测试配置 `settings_test.py` 已覆盖为 LocMemCache,不受影响。

- [ ] **Step 5: 运行相关测试**

Run: `uv run python manage.py test apps.users --settings=config.settings_test -v2`
Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add config/settings.py apps/users/views.py apps/users/tests/test_wechat_replay.py
git commit -m "feat(security): move rate-limit/replay cache to Redis, wire wechat code replay guard"
```

### Task 1.6: 阶段 1 部署验收(不轮换密钥,存量令牌不失效)

- [ ] **Step 1: 本地全量测试**

Run: `uv run python manage.py test --settings=config.settings_test -v2`
Expected: 全部 PASS。

- [ ] **Step 2: 静态检查**

Run: `uv run ruff check config apps`
Expected: 无新增错误(或修复后无错误)。

- [ ] **Step 3: 部署前置——在服务器 `~/.env` 追加 `JWT_SIGNING_KEY`(值=当前 SECRET_KEY)**

在阶段 3 未完成前,`~/.env` 仍会被 CI 覆盖,故此值须先加入 GitHub Secret。执行:

```bash
# 读取当前 SECRET_KEY 值(在服务器上,勿外泄),作为 JWT_SIGNING_KEY 的初始值
ssh yecaoyun 'grep ^SECRET_KEY= ~/.env'
# 将同值设置为 GitHub Secret JWT_SIGNING_KEY(在本地用 gh,需已登录)
# gh secret set JWT_SIGNING_KEY --repo fire-disposal/emoguard_project --body '<粘贴上面的值>'
```

并在 `deploy.yml` 的 `.env` 生成块(第 75-87 行)追加一行:`JWT_SIGNING_KEY=${{ secrets.JWT_SIGNING_KEY }}`(阶段 3 会整体重构此块)。

- [ ] **Step 4: 触发部署并验收**

通过 GitHub Actions `workflow_dispatch` 部署后:

```bash
ssh yecaoyun "docker logs --since 5m emoguard-backend 2>&1 | grep -iE 'JWT|error|migrat' | tail -20"
```
Expected: 迁移含 `token_blacklist`;无 `JWT_SIGNING_KEY 未设置` 报错;既有用户请求正常(存量令牌仍有效)。

---

## 阶段 2:小程序 P0 熔断修复(需过审发版)

小程序无自动化测试框架,采用人工验证清单。

### Task 2.1: 修复 authCenter 熔断计数

**Files:**
- Modify: `miniprogram/utils/authCenter.js:93-127`

- [ ] **Step 1: 修正 refreshToken 的 catch 分支**

将 `refreshToken` 内 catch 块替换为(去掉错误的 `else` 强制赋值,达阈值才熔断;并区分网络错误与令牌失效):

```javascript
    } catch (e) {
      const authFailed = /401|invalid|expired|breakdown|Unauthorized/i.test(e && e.message || '');
      if (authFailed) {
        // 令牌确已失效:立即熔断并跳登录
        breakdown();
      } else {
        // 网络等临时错误:仅累加,达阈值才熔断
        refreshFailCount++;
        if (refreshFailCount >= MAX_REFRESH_FAIL) breakdown();
      }
      reject(e);
    } finally {
      refreshLock = false;
      loginPromise = null;
    }
```

- [ ] **Step 2: 暴露强制登录方法**

在 `authCenter.js` 的 `module.exports` 对象中新增导出:`navigateToLogin,`(供 request.js 在熔断态下主动跳转)。

- [ ] **Step 3: request.js 熔断态主动跳登录**

将 `miniprogram/utils/request.js:41-56` 的 401 处理块中,熔断早退分支替换为:

```javascript
        if (statusCode === 401 && !skipAuth) {
          if (!authCenter.access || authCenter.breakdown) {
            authCenter.navigateToLogin();
            reject(new Error('Token expired and refresh breakdown'));
            return;
          }
```

- [ ] **Step 4: 人工验证清单**

在微信开发者工具中:
1. 登录成功后,手动清空/篡改本地 `refresh_token`(Storage 面板),触发一次接口 401。
   Expected: 自动跳转登录页,提示重新登录,不再卡在"提交失败,请重试"。
2. 断网后提交晚间测试。
   Expected: 提示网络不稳定;恢复网络重试可成功;多次网络失败后才熔断。
3. 正常晚间测试提交。
   Expected: 成功,`eveningFilled=true`。

- [ ] **Step 5: Commit**

```bash
git add miniprogram/utils/authCenter.js miniprogram/utils/request.js
git commit -m "fix(miniapp): route to login on auth breakdown, correct refresh circuit-breaker"
```

- [ ] **Step 6: 发版**

提交微信小程序审核并发布;发布说明标注"修复令牌过期后无法重新登录导致的提交失败"。

---

## 阶段 3:密钥迁移(GitHub Secrets → 服务器手动 `.env`)

**前置条件:阶段 1 已上线(`JWT_SIGNING_KEY` 已在 `~/.env` 中生效)。**

### Task 3.1: 固化并备份服务器 `~/.env`

- [ ] **Step 1: 校验现有 `~/.env` 键完整**

Run: `ssh yecaoyun "cut -d= -f1 ~/.env | sort"`
Expected: 含 `COMPOSE_BAKE, DJANGO_SUPERUSER_EMAIL/PASSWORD/USERNAME, HOST_APP_ROOT, JWT_SIGNING_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY, WECHAT_MINI_PROGRAM_APP_ID/SECRET, WECHAT_SUBSCRIPTION_TEMPLATES`(共 12 项)。若缺 `JWT_SIGNING_KEY`,先补齐(值=SECRET_KEY)。

- [ ] **Step 2: 离线加密备份(禁止进 git)**

由运维将 `~/.env` 内容保存至密码管理器 / sops 加密文件。记录 `POSTGRES_PASSWORD` 已固化进 `emoguard_pg_data` 数据卷,迁移时**严禁改值**。

- [ ] **Step 3: 服务器 `~/.env` 追加静态非密项(确保 CI 不再注入后仍完整)**

Run(确认这两项已存在,缺则补):
```bash
ssh yecaoyun "grep -E '^(HOST_APP_ROOT|COMPOSE_BAKE)=' ~/.env || true"
```
Expected: `HOST_APP_ROOT=/var/www/emoguard` 与 `COMPOSE_BAKE=true` 均在。

### Task 3.2: 改造 deploy.yml 停止重写 `.env`

**Files:**
- Modify: `.github/workflows/deploy.yml:68-93`

- [ ] **Step 1: 移除 `.env` 生成与上传**

将 "Render & Upload Stack Files" 步骤(第 68-93 行)替换为仅渲染并上传 compose、不再触碰 `.env`:

```yaml
      - name: Render & Upload Stack Files
        run: |
          set -euo pipefail

          sed "s|__IMAGE__|${{ steps.ver.outputs.IMAGE }}|g" \
            docker-compose.yml > docker-compose.rendered.yml

          echo "📤 Uploading compose to server (server-side ~/.env is manually managed, untouched)..."
          scp -i ~/.ssh/id_rsa docker-compose.rendered.yml \
            ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }}:~/docker-compose.yml
```

> `Deploy Stack via SSH` 步骤保持不变——它已用 `--env-file ~/.env`,读取的正是服务器手动维护的文件。

- [ ] **Step 2: 语法自检**

Run: `uv run python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/deploy.yml',encoding='utf-8')); print('yaml ok')"`
Expected: `yaml ok`。

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: stop overwriting server .env; manage runtime secrets manually on host"
```

- [ ] **Step 4: 部署验证(关键)**

触发一次部署后:
```bash
ssh yecaoyun "stat -c '%y' ~/.env; docker exec emoguard-backend printenv JWT_SIGNING_KEY >/tmp/k 2>/dev/null; wc -c /tmp/k; rm -f /tmp/k"
```
Expected: `~/.env` 的修改时间**未被本次部署更新**(证明 CI 不再覆盖);容器内 `JWT_SIGNING_KEY` 仍有值;服务健康。

### Task 3.3: 删除 GitHub 中的运行时密钥

**仅在 Task 3.2 Step 4 验证通过后执行。**

- [ ] **Step 1: 逐一删除运行时 Secrets**

在本地(已 `gh auth login`)执行,删除 8 个运行时密钥;保留部署必须的 `SERVER_SSH_KEY / SERVER_HOST / SERVER_USER`(`GITHUB_TOKEN` 为自动注入):

```bash
for s in SECRET_KEY JWT_SIGNING_KEY POSTGRES_PASSWORD REDIS_PASSWORD \
         DJANGO_SUPERUSER_USERNAME DJANGO_SUPERUSER_EMAIL DJANGO_SUPERUSER_PASSWORD \
         WECHAT_MINI_PROGRAM_APP_ID WECHAT_MINI_PROGRAM_APP_SECRET WECHAT_SUBSCRIPTION_TEMPLATES; do
  gh secret delete "$s" --repo fire-disposal/emoguard_project || true
done
```

> `JWT_SIGNING_KEY` 一并从 GitHub 删除,因其已常驻服务器 `~/.env`。

- [ ] **Step 2: 确认残留仅部署必须项**

Run: `gh secret list --repo fire-disposal/emoguard_project`
Expected: 仅剩 `SERVER_SSH_KEY, SERVER_HOST, SERVER_USER`(及仓库级自动 token 不在列表)。

- [ ] **Step 3: 冒烟部署**

再次 `workflow_dispatch` 部署一次,确认在无运行时 Secrets 情况下仍成功(因 `.env` 全由服务器提供)。
Expected: 健康检查通过,`~/.env` 未被改动。

### Task 3.4: 文档与模板更新

**Files:**
- Modify: `.env.example`
- Modify: `README.md`(如存在部署章节)

- [ ] **Step 1: 更新 `.env.example`**

追加缺失项,使模板与服务器实际键一致:

```
POSTGRES_PASSWORD=你的数据库密码
REDIS_PASSWORD=你的Redis密码
SECRET_KEY=你的Django密钥
JWT_SIGNING_KEY=你的JWT签名密钥（与SECRET_KEY解耦，独立管理）
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=强密码
WECHAT_MINI_PROGRAM_APP_ID=你的微信小程序AppID
WECHAT_MINI_PROGRAM_APP_SECRET=你的微信小程序AppSecret
WECHAT_SUBSCRIPTION_TEMPLATES=你的微信订阅消息模板ID
HOST_APP_ROOT=/var/www/emoguard
COMPOSE_BAKE=true
```

- [ ] **Step 2: 记录运维约定**

在 README 部署章节补充:`~/.env` 为服务器手动维护的运行时密钥来源,CI 不再生成/覆盖;新增/轮换运行时密钥须直接编辑服务器 `~/.env` 并 `docker compose --env-file ~/.env up -d`;GitHub 仅保留 SSH/GHCR 部署密钥;`.env` 须离线加密备份。

- [ ] **Step 3: Commit**

```bash
git add .env.example README.md
git commit -m "docs: document manual server-side .env management and JWT_SIGNING_KEY"
```

---

## Self-Review 覆盖对照

- P0 客户端熔断 → Task 2.1 ✓
- 令牌日志脱敏 + 降级日志级别 → Task 1.4 ✓
- 独立 JWT_SIGNING_KEY + fail-fast → Task 1.1 ✓
- access 时长缩短(24h)→ Task 1.1 ✓
- 单一刷新端点契约 + 旋转 → Task 1.3(`/api/token/refresh/` 为客户端唯一入口,行为一致)✓
- 限流/防重放迁 Redis + 死代码接入 → Task 1.5 ✓
- token_blacklist 真轮换/可吊销 → Task 1.2 + 1.3 ✓
- 密钥迁移(停写 .env → 删 Secrets)顺序安全 → Task 3.2 先于 3.3 ✓
- POSTGRES_PASSWORD 固化风险 → Task 3.1 Step 2 明确不改值 ✓
