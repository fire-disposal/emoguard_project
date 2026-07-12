# EmoGuard 系统性修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不扩张资源、不破坏可用性、不改变现有设计范式的前提下，全量修复审计发现的功能性 BUG、越权(IDOR)、竞态与稳定性风险。

**Architecture:** Django 5.2 + Django-Ninja-Extra 单体后端，单 Gunicorn worker，Celery worker 内嵌 beat（`-B`），单 Redis，PostgreSQL/SQLite。所有修复必须保持此资源画像不变。

**Tech Stack:** Django 5.2、django-ninja(-extra/-jwt)、Celery 5.5、Redis、PostgreSQL 15、uv、ruff。

---

## 核心约束（每个任务都必须遵守）

1. **可用性优先于安全性**：任何加认证/校验的改动，都必须先确认不会拒绝小程序当前发送的合法请求。已核实：小程序对所有后端调用（除 `/api/users/wechat/login`、`/api/token/refresh/`）均携带 `Authorization: Bearer`（证据 `miniprogram/utils/request.js:22-29`）。
2. **不扩张资源**：禁止增加 Gunicorn worker 数、禁止拆分 Celery beat 独立容器、禁止新增 Redis 逻辑库、禁止无必要的新依赖。
3. **不做大范围范式变动**：沿用现有 `request.auth`/`request.user`、`HttpError`、手工构造 Schema 等既有写法。
4. **应修尽修**：本计划覆盖全部审计条目；确因用户决策排除的项在“不修复项”中登记。

## 输入范围（防止校验误伤合法请求，来自小程序源码核实）

| 字段 | 端点 | min | max | 必填 |
|------|------|-----|-----|------|
| depression | POST /api/emotiontracker/ | 0 | 3 | 是 |
| anxiety | POST /api/emotiontracker/ | 0 | 10 | 是 |
| energy | POST /api/emotiontracker/ | 0 | 3 | 是 |
| sleep | POST /api/emotiontracker/ | 0 | 4 | 是 |
| moodIntensity | POST /api/emotiontracker/ | 1 | 3 | 是 |
| moodIntensity | POST /api/journals/ | 1 | 10 | 是（不同范围！） |
| rating | POST /api/feedback/feedback | 1 | 5 | 是 |
| content | POST /api/feedback/feedback | 0 | 500 字 | 否 |

> 校验边界必须**按端点作用域**设置，且取**宽松上界**（见下）。EMA 与日记的 `moodIntensity` 范围不同，绝不可共用一个 0-10 之外的收窄区间。为最大化可用性，EMA 数值统一采用宽松上界 `ge=0, le=100`，仅防脏数据（负数/超大值），不卡业务细分上界。

## 不修复项（用户决策 / 明确排除，登记备查）

- **不新增 ScaleConfig 模型、不实现 PHQ-9/MoCA/MMSE/SCD/ADL 计分类**：维持 README 现状（仅 GAD-7 走 registry）。
- **不新增 Gunicorn worker / 不拆分 beat / 不加 Redis 库**：资源约束。
- **不引入新的 HTML 消毒依赖**：管理端 XSS 用 Django 内置 `format_html` 转义修复（Task 5.2），不加 nh3/bleach。

---

## 阶段总览

- **Phase 0**：测试基线（确保 `settings_test` 可跑、迁移无漂移）
- **Phase 1**：可用性/正确性 BUG（无安全副作用，最安全，先做）
- **Phase 2**：越权(IDOR)与认证加固（已核实不影响小程序）
- **Phase 3**：稳定性与资源（微信 token 缓存＝省资源、竞态、幂等）
- **Phase 4**：清理（ruff、乱码、死管线、管理端 XSS）

每个阶段结束后运行：
```
uv run python manage.py test --settings=config.settings_test
uv run python manage.py check --settings=config.settings_test
uv run ruff check .
```

---

# Phase 0 — 测试基线

### Task 0.1: 确认基线可运行

**Files:**
- 只读验证，无改动

- [ ] **Step 1: 运行现有测试**

Run: `uv run python manage.py test --settings=config.settings_test`
Expected: `Ran 4 tests ... OK`

- [ ] **Step 2: 确认无迁移漂移（业务 app）**

Run: `uv run python manage.py makemigrations --check --dry-run apps.users apps.articles apps.journals apps.reports apps.scales apps.notice apps.emotiontracker apps.feedback apps.cognitive_flow --settings=config.settings_test`
Expected: 退出码 0（不应有待生成迁移；django_summernote 的第三方漂移与本项目无关，忽略）

- [ ] **Step 3: 基线 ruff**

Run: `uv run ruff check .`
Expected: 记录当前 6 处 F401（Phase 4 修复）

---

# Phase 1 — 可用性 / 正确性 BUG

### Task 1.1: EMA 用户状态更新的静默吞异常 + 事务一致性

**问题**：`apps/emotiontracker/views.py:60-78` 的 `except Exception: pass` 吞掉用户完成标志更新失败；且 `created_at` 被塞进 `defaults` 覆盖 `auto_now_add`。

**Files:**
- Modify: `apps/emotiontracker/views.py:35-78`

- [ ] **Step 1: 移除 defaults 中的 created_at，记录异常而非吞掉**

将 `defaults_data`（第 35-46 行）中的 `"created_at": timezone.now()` 一行删除：

```python
    defaults_data = {
        "depression": data.depression,
        "anxiety": data.anxiety,
        "energy": data.energy,
        "sleep": data.sleep,
        "mainMood": getattr(data, "mainMood", None),
        "moodIntensity": getattr(data, "moodIntensity", None),
        "mainMoodOther": getattr(data, "mainMoodOther", None),
        "moodSupplementTags": getattr(data, "moodSupplementTags", None),
        "moodSupplementText": getattr(data, "moodSupplementText", None),
    }
```

- [ ] **Step 2: 将静默 `except Exception: pass` 改为记录日志（不改变对外行为，仅可观测）**

把第 59-78 行的 try/except 改为：

```python
    # 更新用户上次测试时间和完成情况
    import logging
    _logger = logging.getLogger("emotiontracker.views")
    try:
        today = timezone.localtime().date()
        update_data = {
            'last_mood_tested_at': timezone.now(),
            'last_completion_reset_date': today
        }
        if period == EmotionRecord.PERIOD_MORNING:
            update_data['morning_completed_today'] = True
        elif period == EmotionRecord.PERIOD_EVENING:
            update_data['evening_completed_today'] = True
        User.objects.filter(id=current_user.id).update(**update_data)
    except Exception as exc:
        _logger.error("更新用户情绪完成状态失败: user_id=%s, err=%s", current_user.id, exc, exc_info=True)
```

- [ ] **Step 3: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 4: Commit**

```
git add apps/emotiontracker/views.py
git commit -m "fix(emotiontracker): stop overwriting created_at and log profile-update failures instead of swallowing"
```

---

### Task 1.2: 情绪日记日统计的时区跨天分组 BUG

**问题**：`apps/journals/views.py:172-180` 用 `record_date__date`（按 UTC 截断），CST 晚间记录会落入前一天。改用带时区的 `TruncDate`。

**Files:**
- Modify: `apps/journals/views.py:1-12`（导入）、`162-200`

- [ ] **Step 1: 增加导入**

在文件顶部导入区（第 4 行 `from django.db.models import Avg, Count` 之后）追加：

```python
from django.db.models.functions import TruncDate
```

- [ ] **Step 2: 用本地时区 TruncDate 重写日统计聚合**

将 `get_daily_statistics`（第 162-200 行）主体替换为：

```python
@journals_router.get("/statistics/daily", response=list[MoodStatisticsSchema], auth=jwt_auth)
def get_daily_statistics(request, days: int = Query(30, ge=1, le=365)):
    """获取当前用户的日情绪统计"""
    current_user = request.auth
    tz = timezone.get_current_timezone()
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days - 1)

    statistics = (
        MoodJournal.objects.filter(user_id=current_user.id)
        .annotate(local_date=TruncDate('record_date', tzinfo=tz))
        .filter(local_date__gte=start_date, local_date__lte=end_date)
        .values('local_date')
        .annotate(avg_score=Avg('moodIntensity'), mood_count=Count('id'))
        .order_by('local_date')
    )

    result = []
    for stat in statistics:
        dominant_mood = (
            MoodJournal.objects.filter(user_id=current_user.id)
            .annotate(local_date=TruncDate('record_date', tzinfo=tz))
            .filter(local_date=stat['local_date'])
            .values('mainMood')
            .annotate(count=Count('id'))
            .order_by('-count')
            .first()
        )
        result.append(MoodStatisticsSchema(
            date=stat['local_date'].isoformat(),
            avg_score=round(stat['avg_score'], 2) if stat['avg_score'] is not None else 0,
            mood_count=stat['mood_count'],
            dominant_mood=dominant_mood['mainMood'] if dominant_mood and dominant_mood['mainMood'] else '未知'
        ))
    return result
```

> 说明：同时修复了 `avg_score` 为 None（该日 `moodIntensity` 全空）时 `round(None)` 崩溃的隐患。

- [ ] **Step 3: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 4: Commit**

```
git add apps/journals/views.py
git commit -m "fix(journals): group daily stats by local date via TruncDate and guard null avg"
```

---

### Task 1.3: `days` 参数无上限 (DoS) — 统一加范围约束

**问题**：`emotiontracker/views.py:121`、`journals/views.py:203`、`reports/views.py:225` 的 `days` 无上限。Task 1.2 已修 `get_daily_statistics`。

**Files:**
- Modify: `apps/emotiontracker/views.py:120-121`
- Modify: `apps/journals/views.py:202-203`
- Modify: `apps/reports/views.py:224-225`

- [ ] **Step 1: emotiontracker trend**

`apps/emotiontracker/views.py` 顶部第 1 行确认已 `from ninja import Router`，改为：
```python
from ninja import Router, Query
```
将第 120-121 行签名改为：
```python
@emotion_router.get("/trend", response=EmotionTrendSchema, auth=jwt_auth)
def get_emotion_trend(request, days: int = Query(30, ge=1, le=365)):
```

- [ ] **Step 2: journals mood trends**

`apps/journals/views.py` 第 202-203 行改为：
```python
@journals_router.get("/trends/score", response=dict, auth=jwt_auth)
def get_mood_trends(request, days: int = Query(30, ge=1, le=365)):
```

- [ ] **Step 3: reports health trends**

`apps/reports/views.py` 第 224-225 行改为：
```python
@reports_router.get("/trends", response=list[HealthTrendSchema], auth=jwt_auth)
def get_health_trends(request, days: int = Query(90, ge=1, le=365)):
```

- [ ] **Step 4: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 5: Commit**

```
git add apps/emotiontracker/views.py apps/journals/views.py apps/reports/views.py
git commit -m "fix(api): cap days query param to 1..365 to prevent unbounded range DoS"
```

---

### Task 1.4: 情绪 / 反馈输入的宽松边界校验（防脏数据，不误伤）

**问题**：`depression/anxiety/energy/sleep` 与 `rating` 无范围校验，`objects.create` 不触发 model validator。用宽松边界仅拦截明显非法值。

**Files:**
- Modify: `apps/emotiontracker/serializers.py:1-13`
- Modify: `apps/feedback/serializers.py:1-9`

- [ ] **Step 1: EMA 创建 Schema 加宽松边界**

将 `apps/emotiontracker/serializers.py` 顶部导入区（第 1-2 行）替换为：

```python
from ninja import Schema, Field
from typing import List, Optional
```

再将 `EmotionRecordCreateSchema`（第 4-13 行）替换为：

```python
class EmotionRecordCreateSchema(Schema):
    depression: int = Field(ge=0, le=100)
    anxiety: int = Field(ge=0, le=100)
    energy: int = Field(ge=0, le=100)
    sleep: int = Field(ge=0, le=100)
    mainMood: Optional[str] = None
    moodIntensity: Optional[int] = Field(default=None, ge=0, le=100)
    mainMoodOther: Optional[str] = None
    moodSupplementTags: Optional[list] = None
    moodSupplementText: Optional[str] = None
```

> 上界取 100（远超业务 0-10），只拦负数/超大脏数据，绝不误伤合法值。`List` 仍被 `EmotionTrendSchema` 使用，保留导入。

- [ ] **Step 2: 反馈 Schema 加 1-5 边界（小程序已保证 1-5，边界安全）**

将 `apps/feedback/serializers.py` 顶部导入区（第 2-3 行）替换为：

```python
from ninja import Schema, Field
from typing import Optional
```

再将 `FeedbackCreateSchema`（第 6-9 行）替换为：

```python
class FeedbackCreateSchema(Schema):
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = Field(default=None, max_length=500)
```

- [ ] **Step 3: 写失败测试再验证通过**

Create: `apps/feedback/tests/__init__.py`（空文件）
Create: `apps/feedback/tests/test_rating_validation.py`

```python
from django.test import TestCase
from apps.feedback.serializers import FeedbackCreateSchema
from pydantic import ValidationError


class RatingValidationTest(TestCase):
    def test_rating_zero_rejected(self):
        with self.assertRaises(ValidationError):
            FeedbackCreateSchema(rating=0)

    def test_rating_six_rejected(self):
        with self.assertRaises(ValidationError):
            FeedbackCreateSchema(rating=6)

    def test_rating_valid(self):
        obj = FeedbackCreateSchema(rating=5, content="ok")
        self.assertEqual(obj.rating, 5)
```

- [ ] **Step 4: 运行测试**

Run: `uv run python manage.py test apps.feedback --settings=config.settings_test`
Expected: PASS

- [ ] **Step 5: Commit**

```
git add apps/emotiontracker/serializers.py apps/feedback/serializers.py apps/feedback/tests/
git commit -m "fix(validation): add lenient score bounds and enforce feedback rating 1-5"
```

---

### Task 1.5: 无分页的无界列表 — 加显式上限（保持返回结构不变）

**问题**：`emotiontracker/views.py:98`、`feedback/views.py:28`、`cognitive_flow/views.py:89` 一次性返回全部记录。为不改变现有响应结构（数组），仅在查询层加合理硬上限切片，避免范式变动。

**Files:**
- Modify: `apps/emotiontracker/views.py:98-101`
- Modify: `apps/feedback/views.py:27-38`
- Modify: `apps/cognitive_flow/views.py:89-96`

- [ ] **Step 1: emotiontracker 列表加上限**

`apps/emotiontracker/views.py` 第 101 行 `queryset = ...order_by("-created_at")` 改为：
```python
    queryset = EmotionRecord.objects.filter(user_id=current_user.id).order_by("-created_at")[:500]
```

- [ ] **Step 2: feedback 列表加上限**

`apps/feedback/views.py` 第 30 行改为：
```python
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')[:200]
```

- [ ] **Step 3: cognitive 历史加上限**

`apps/cognitive_flow/views.py` 第 96 行改为：
```python
        records = CognitiveAssessmentRecord.objects.filter(user_id=user_id).order_by("-created_at")[:200]
```

- [ ] **Step 4: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 5: Commit**

```
git add apps/emotiontracker/views.py apps/feedback/views.py apps/cognitive_flow/views.py
git commit -m "fix(api): cap unbounded list endpoints to hard limits to avoid memory blowups"
```

---

### Task 1.6: 量表提交重复计算 + 调试信息泄漏

**问题**：`apps/scales/views.py:69,74` 计分跑两遍；`:66-68,93-113` 把 `str(data)` 泄漏给客户端。

**Files:**
- Modify: `apps/scales/views.py:54-113`

- [ ] **Step 1: 删除重复 calculate，去除响应中的 debug**

将 `create_scale_result`（第 54-113 行）替换为：

```python
@scales_router.post("/results", auth=jwt_auth, response=Dict[str, Any])
def create_scale_result(request, data: ScaleResultCreateSchema):
    """提交量表结果"""
    try:
        user_id = str(request.user.id)
        ScaleRegistry.discover_scales()
        scale_obj = ScaleRegistry.get_scale(data.scale_code)
        if not scale_obj:
            logger.error("量表未注册: scale_code=%s", data.scale_code)
            return {"error": "量表未注册"}

        analysis = ScaleRegistry.calculate(data.scale_code, data.selected_options)
        from apps.scales.models import ScaleResult

        result = ScaleResult.objects.create(
            user_id=user_id,
            scale_code=data.scale_code,
            score=analysis.get("score", 0.0),
            selected_options=data.selected_options,
            conclusion=analysis.get("interpretation", ""),
            started_at=data.started_at,
            completed_at=data.completed_at,
        )
        logger.info(
            "量表结果创建成功: id=%s, user_id=%s, scale_code=%s",
            result.id, user_id, data.scale_code,
        )
        return {
            "id": result.id,
            "score": result.score,
            "success": True,
            "message": "量表结果提交成功",
        }
    except Exception as e:
        logger.error("提交量表结果失败: %s", str(e), exc_info=True)
        return {"error": "提交失败"}
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/scales/views.py
git commit -m "fix(scales): remove duplicate scoring call and strip debug payload from responses"
```

---

# Phase 2 — 越权(IDOR) 与认证加固

> 已核实：小程序对以下端点均携带 Bearer token；文章写接口小程序不调用（运营走 Django Admin）。因此以下加固不影响可用性。

### Task 2.1: 文章接口 — 读需登录、写需管理员、列表/详情仅返回已发布（非管理员）

**Files:**
- Modify: `apps/articles/views.py`（全文）
- Modify: `apps/articles/serializers.py:1-12`

- [ ] **Step 1: status 字段用 Literal 约束**

将 `apps/articles/serializers.py` 第 1-12 行替换为：

```python
from ninja import Schema
from typing import Optional, Literal

class ArticleCreateSchema(Schema):
    title: str
    content: str
    status: Literal["draft", "published"] = "draft"

class ArticleUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[Literal["draft", "published"]] = None
```

- [ ] **Step 2: 视图加认证与权限，读接口对非管理员仅返回 published**

将 `apps/articles/views.py` 顶部导入区（第 1-9 行）替换为：

```python
from ninja import Router, Query
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from .models import Article
from .serializers import (
    ArticleCreateSchema, ArticleUpdateSchema, ArticleResponseSchema, ArticleListQuerySchema
)
from config.jwt_auth_adapter import jwt_auth

articles_router = Router(tags=["articles"])


def _require_admin(request):
    if getattr(request.auth, "role", None) != "admin":
        raise HttpError(403, "需要管理员权限")


def _is_admin(request):
    return getattr(request.auth, "role", None) == "admin"
```

- [ ] **Step 3: 列表接口加 auth，非管理员强制 published，并限制 page_size**

将 `list_articles`（原第 11-43 行）替换为：

```python
@articles_router.get("/", response=list[ArticleResponseSchema], auth=jwt_auth)
def list_articles(request, filters: ArticleListQuerySchema = Query(...)):
    """获取文章列表；非管理员仅可见已发布文章"""
    queryset = Article.objects.all()

    if _is_admin(request):
        if filters.status:
            queryset = queryset.filter(status=filters.status)
    else:
        queryset = queryset.filter(status='published')

    if filters.search:
        queryset = queryset.filter(
            Q(title__icontains=filters.search) | Q(content__icontains=filters.search)
        )

    page_size = min(filters.page_size, settings.MAX_PAGE_SIZE)
    start = (filters.page - 1) * page_size
    end = start + page_size
    articles = queryset[start:end]

    return [
        ArticleResponseSchema(
            id=a.id, title=a.title, content=a.content, status=a.status,
            created_at=a.created_at.isoformat(), updated_at=a.updated_at.isoformat()
        )
        for a in articles
    ]
```

- [ ] **Step 4: 详情接口加 auth，非管理员看不到草稿（404）**

将 `get_article`（原第 45-58 行）替换为：

```python
@articles_router.get("/{article_id}", response=ArticleResponseSchema, auth=jwt_auth)
def get_article(request, article_id: int):
    """获取单篇文章详情；非管理员不可见草稿"""
    if _is_admin(request):
        article = get_object_or_404(Article, id=article_id)
    else:
        article = get_object_or_404(Article, id=article_id, status='published')
    return ArticleResponseSchema(
        id=article.id, title=article.title, content=article.content, status=article.status,
        created_at=article.created_at.isoformat(), updated_at=article.updated_at.isoformat()
    )
```

- [ ] **Step 5: 全部写接口加 auth + 管理员校验**

对 `create_article`(第60行)、`update_article`(第80行)、`delete_article`(第106行)、`publish_article`(第115行)、`draft_article`(第125行) 五个装饰器分别追加 `, auth=jwt_auth`，并在各函数体第一行加 `_require_admin(request)`。示例（create）：

```python
@articles_router.post("/", response=ArticleResponseSchema, auth=jwt_auth)
def create_article(request, data: ArticleCreateSchema):
    """创建新文章（管理员）"""
    _require_admin(request)
    article = Article.objects.create(
        title=data.title, content=data.content, status=data.status
    )
    return ArticleResponseSchema(
        id=article.id, title=article.title, content=article.content, status=article.status,
        created_at=article.created_at.isoformat(), updated_at=article.updated_at.isoformat()
    )
```

其余四个同法：装饰器加 `auth=jwt_auth`，函数体首行加 `_require_admin(request)`。

- [ ] **Step 6: 写 IDOR 回归测试**

Create: `apps/articles/tests/__init__.py`（空）
Create: `apps/articles/tests/test_article_auth.py`

```python
from django.test import TestCase, Client
from apps.articles.models import Article


class ArticleAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        Article.objects.create(title="draft-a", content="x", status="draft")

    def test_anonymous_cannot_list(self):
        resp = self.client.get("/api/articles/")
        self.assertIn(resp.status_code, (401, 403))

    def test_anonymous_cannot_create(self):
        resp = self.client.post(
            "/api/articles/", data={"title": "h", "content": "c"},
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (401, 403))
```

- [ ] **Step 7: 运行测试**

Run: `uv run python manage.py test apps.articles --settings=config.settings_test`
Expected: PASS

- [ ] **Step 8: Commit**

```
git add apps/articles/
git commit -m "fix(articles): require auth for reads, admin for writes, hide drafts from non-admins"
```

---

### Task 2.2: 报告详情/改/删 — 加认证与归属过滤

**问题**：`apps/reports/views.py:63,117,155` 无 auth、无 user_id 过滤。小程序仅调用 `GET /api/reports/{id}`（携带 token），故加固安全。

**Files:**
- Modify: `apps/reports/views.py:63-162`

- [ ] **Step 1: get_report 加 auth + 归属**

将第 63-68 行替换为：

```python
@reports_router.get("/{report_id}", response=HealthReportResponseSchema, auth=jwt_auth)
def get_report(request, report_id: int):
    """获取单份健康报告详情（仅本人）"""
    report = get_object_or_404(HealthReport, id=report_id, user_id=request.auth.id)
```

- [ ] **Step 2: update_report 加 auth + 归属**

将第 117-122 行替换为：

```python
@reports_router.put("/{report_id}", response=HealthReportResponseSchema, auth=jwt_auth)
def update_report(request, report_id: int, data: HealthReportUpdateSchema):
    """更新健康报告（仅本人）"""
    report = get_object_or_404(HealthReport, id=report_id, user_id=request.auth.id)
```

- [ ] **Step 3: delete_report 加 auth + 归属**

将第 155-162 行替换为：

```python
@reports_router.delete("/{report_id}", auth=jwt_auth)
def delete_report(request, report_id: int):
    """删除健康报告（仅本人）"""
    report = get_object_or_404(HealthReport, id=report_id, user_id=request.auth.id)
    report.delete()
    return {"success": True}
```

> 注意：`/{report_id}` 与 `/summary`、`/trends` 共存。因 `report_id: int` 使用整数路径转换器，非数字路径（`summary`/`trends`）不会被 `/{report_id}` 捕获，二者可安全共存（Step 4 有集成测试佐证）。

- [ ] **Step 4: 加集成测试验证 IDOR 已封堵**

Create: `apps/reports/tests/__init__.py`（空）
Create: `apps/reports/tests/test_reports_auth.py`

```python
from django.test import TestCase, Client
from apps.reports.models import HealthReport


class ReportsAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        HealthReport.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            assessment_id=1, report_type="t", overall_risk="低风险",
            summary="s", recommendations=[], professional_advice="a",
            trend_analysis="ta", trend_data={},
        )

    def test_anonymous_cannot_get_report(self):
        resp = self.client.get("/api/reports/1")
        self.assertIn(resp.status_code, (401, 403))
```

- [ ] **Step 5: 运行测试**

Run: `uv run python manage.py test apps.reports --settings=config.settings_test`
Expected: PASS

- [ ] **Step 6: Commit**

```
git add apps/reports/
git commit -m "fix(reports): require auth and owner scoping on report detail/update/delete (IDOR)"
```

---

### Task 2.3: 日记详情 — 加认证与归属过滤

**问题**：`apps/journals/views.py:60` 无 auth、无归属。小程序未调用该端点，加固零风险。

**Files:**
- Modify: `apps/journals/views.py:60-75`

- [ ] **Step 1: get_journal 加 auth + 归属**

将第 60-65 行替换为：

```python
@journals_router.get("/{journal_id}", response=MoodJournalResponseSchema, auth=jwt_auth)
def get_journal(request, journal_id: int):
    """获取单条情绪日记详情（仅本人）"""
    journal = get_object_or_404(MoodJournal, id=journal_id, user_id=request.auth.id)
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/journals/views.py
git commit -m "fix(journals): require auth and owner scoping on journal detail (IDOR)"
```

---

### Task 2.4: 量表结果详情 — 加认证与归属过滤

**问题**：`apps/scales/views.py:176` 无 auth、`filter(id=result_id)` 无 user_id。小程序调用该端点并携带 token。

**Files:**
- Modify: `apps/scales/views.py:176-184`

- [ ] **Step 1: get_scale_result 加 auth + 归属**

将第 176-184 行替换为：

```python
@scales_router.get("/results/{result_id}", response=ScaleResultResponseSchema, auth=jwt_auth)
def get_scale_result(request, result_id: int):
    """获取单量表结果详情（仅本人）"""
    try:
        from apps.scales.models import ScaleResult

        result = ScaleResult.objects.filter(id=result_id, user_id=str(request.user.id)).first()
        if not result:
            return {"error": "结果不存在"}
```

（其余函数体保持不变。）

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/scales/views.py
git commit -m "fix(scales): require auth and owner scoping on scale result detail (IDOR)"
```

---

### Task 2.5: 用户列表/详情 — 限管理员

**问题**：`apps/users/views.py:211,221` 任意登录用户可拉全量用户。小程序不调用（仅 `/me` 系）。

**Files:**
- Modify: `apps/users/views.py:211-225`

- [ ] **Step 1: list_users 与 get_user 加管理员校验**

将第 211-225 行替换为：

```python
@users_router.get("/users", response=list[UserResponseSchema], auth=jwt_auth)
def list_users(request, role=None):
    """获取用户列表（仅管理员），支持按角色过滤"""
    if request.auth.role != "admin":
        raise HttpError(403, "需要管理员权限")
    queryset = User.objects.all()
    if role:
        queryset = queryset.filter(role=role)
    return [_user_to_response_schema(u) for u in queryset]


@users_router.get("/users/{user_id}", response=UserResponseSchema, auth=jwt_auth)
def get_user(request, user_id):
    """获取单个用户信息（仅管理员或本人）"""
    if request.auth.role != "admin" and str(request.auth.id) != str(user_id):
        raise HttpError(403, "无权限查看其他用户")
    user = get_object_or_404(User, id=user_id)
    return _user_to_response_schema(user)
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/users/views.py
git commit -m "fix(users): restrict user list/detail to admin or self (IDOR)"
```

---

### Task 2.6: 微信 code 防重放 TOCTOU — 改原子 cache.add

**问题**：`apps/users/wechat_auth.py:129-132` 先 get 再 set 非原子。

**Files:**
- Modify: `apps/users/wechat_auth.py:118-133`

- [ ] **Step 1: 用 cache.add 原子占位**

将 `validate_wechat_code`（第 118-133 行）主体替换为：

```python
    def validate_wechat_code(self, code):
        """验证微信登录凭证 code 是否已使用（原子 SET NX 防并发重放）"""
        cache_key = f"wechat_code_{code}"
        # cache.add 在 Redis 上是原子 SET NX；返回 False 表示 key 已存在（已用过）
        if not cache.add(cache_key, True, 300):
            raise Exception("微信登录凭证已使用")
        logger.info("微信code验证通过: %s...", code[:10])
```

- [ ] **Step 2: 复用既有重放测试验证**

Run: `uv run python manage.py test apps.users.tests.test_wechat_replay --settings=config.settings_test`
Expected: PASS

- [ ] **Step 3: Commit**

```
git add apps/users/wechat_auth.py
git commit -m "fix(users): use atomic cache.add for wechat code replay guard (TOCTOU)"
```

---

### Task 2.7: 微信新用户创建竞态 — get_or_create 收敛

**问题**：`apps/users/wechat_auth.py:147-190` 的 `get()` 在事务外，并发首登抛未捕获 IntegrityError → 500。

**Files:**
- Modify: `apps/users/wechat_auth.py:135-191`

- [ ] **Step 1: 用 get_or_create 处理竞态**

将 `get_or_create_user`（第 135-191 行）替换为：

```python
    def get_or_create_user(self, openid, unionid=None, user_info=None):
        """根据 openid 获取或创建用户（并发安全）"""
        gender = ''
        if user_info:
            gender = self._convert_gender(user_info.get('gender'))

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                wechat_openid=openid,
                defaults={
                    'username': openid,
                    'wechat_unionid': unionid,
                    'role': 'user',
                    'gender': gender,
                },
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
                logger.info("创建新微信用户: %s", openid)
                return user, True

        # 已存在：按需更新 unionid / gender
        update_fields = []
        if unionid and user.wechat_unionid != unionid:
            user.wechat_unionid = unionid
            update_fields.append('wechat_unionid')
        if user_info and not user.gender and user_info.get('gender'):
            user.gender = self._convert_gender(user_info.get('gender'))
            update_fields.append('gender')
        if update_fields:
            user.save(update_fields=update_fields)
            logger.info("更新用户信息: %s, 字段: %s", openid, update_fields)
        return user, False
```

- [ ] **Step 2: 验证登录测试仍通过**

Run: `uv run python manage.py test apps.users --settings=config.settings_test`
Expected: PASS

- [ ] **Step 3: Commit**

```
git add apps/users/wechat_auth.py
git commit -m "fix(users): make wechat user creation concurrency-safe via get_or_create"
```

---

### Task 2.8: 限流原子计数 + 覆盖无斜杠刷新端点 + 中间件异常收窄

**问题**：`apps/users/rate_limit.py` 计数非原子（`:37-44`）；中间件仅匹配 `/api/token/refresh/`（`:77`）；`except Exception` 过宽（`:81`，Redis 挂会自 DoS）。保持 XFF 现状（Nginx 后合理），不改信任模型以免误伤。

**Files:**
- Modify: `apps/users/rate_limit.py:23-49`、`76-84`

- [ ] **Step 1: 计数改原子 incr**

将 `wrapped_view`（第 24-46 行）中“获取当前计数/增加计数”部分替换为：

```python
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            cache_key = f"rate_limit:{key_prefix}:{ip}"

            # 原子递增；首次用 add 建立窗口，避免 get+set 竞态
            try:
                current = cache.incr(cache_key)
            except ValueError:
                cache.add(cache_key, 1, window_seconds)
                current = 1

            if current > max_requests:
                logger.warning("频率限制触发: %s -> %s", ip, key_prefix)
                raise HttpError(429, "请求过于频繁，请稍后重试")

            return view_func(request, *args, **kwargs)
```

- [ ] **Step 2: 中间件匹配两种路径，异常收窄到 HttpError**

将 `RefreshTokenRateLimitMiddleware.__call__`（第 76-84 行）替换为：

```python
    def __call__(self, request):
        if request.path in ("/api/token/refresh/", "/api/token/refresh"):
            try:
                refresh_token_rate_limit(lambda req: None)(request)
            except HttpError:
                from django.http import JsonResponse
                return JsonResponse({"detail": "请求过于频繁，请稍后重试"}, status=429)
            # 其它异常（如缓存后端故障）不拦截，放行以保可用性
        return self.get_response(request)
```

> 关键：Redis 故障时**放行**而非返回 429，符合“可用性优先于安全性”。

- [ ] **Step 3: 复用既有刷新限流测试**

Run: `uv run python manage.py test apps.users.tests.test_token_refresh --settings=config.settings_test`
Expected: PASS

- [ ] **Step 4: Commit**

```
git add apps/users/rate_limit.py
git commit -m "fix(ratelimit): atomic incr, cover slashless refresh path, fail-open on cache errors"
```

---

### Task 2.9: create_admin 修复 role 与密码日志泄漏

**问题**：`create_admin.py:78` 未设 `role='admin'`（导致 API 登录 403）；`:64,91` 明文打印密码。

**Files:**
- Modify: `apps/users/management/commands/create_admin.py:78-95`

- [ ] **Step 1: create_superuser 显式设 role，并停止打印密码**

将第 77-95 行替换为：

```python
            # 创建新管理员
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role='admin',
            )

            self.stdout.write(
                self.style.SUCCESS(f'成功创建管理员账户: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'邮箱: {email}')
            )
            self.stdout.write(
                self.style.WARNING('请通过环境变量 DJANGO_SUPERUSER_PASSWORD 设置的密码登录，并及时修改。')
            )
```

- [ ] **Step 2: 同步移除 --force 分支的密码打印（第 63-65 行）**

将第 63-65 行的：
```python
                    self.stdout.write(
                        self.style.WARNING(f'密码: {password}')
                    )
```
替换为：
```python
                    self.stdout.write(
                        self.style.WARNING('密码已重置为环境变量提供的值，请及时修改。')
                    )
```

- [ ] **Step 3: 验证命令可导入**

Run: `uv run python manage.py help create_admin --settings=config.settings_test`
Expected: 显示帮助，无错误

- [ ] **Step 4: Commit**

```
git add apps/users/management/commands/create_admin.py
git commit -m "fix(users): set role=admin on superuser creation and stop logging plaintext password"
```

---

# Phase 3 — 稳定性与资源

### Task 3.1: 微信 access_token 缓存（省资源 + 防配额耗尽）

**问题**：`apps/notice/services.py:11-26` 每次推送都请求 token，日额度 ~2000 次会被耗尽。用 Django cache（复用现有 Redis，不新增库）缓存 ~7000s。

**Files:**
- Modify: `apps/notice/services.py:1-26`

- [ ] **Step 1: 缓存 token**

将第 1-26 行替换为：

```python
import requests
from urllib.parse import urlencode
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
import logging
from .models import UserQuota, NotificationLog

logger = logging.getLogger("notice.services")

_WECHAT_TOKEN_CACHE_KEY = "wechat:access_token"


def get_wechat_access_token(force_refresh=False):
    """获取微信 access_token（缓存 ~7000s，复用现有 Redis，避免每次请求耗尽日配额）"""
    if not force_refresh:
        cached = cache.get(_WECHAT_TOKEN_CACHE_KEY)
        if cached:
            return cached

    appid = settings.WECHAT_MINI_PROGRAM_APP_ID
    secret = settings.WECHAT_MINI_PROGRAM_APP_SECRET
    params = urlencode({
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret,
    })
    url = f"https://api.weixin.qq.com/cgi-bin/token?{params}"

    try:
        response = requests.get(url, timeout=5)
        result = response.json()
    except Exception as e:
        # 不记录 url（含 secret），仅记录异常类型
        logger.error("获取access_token失败: %s", type(e).__name__)
        return None

    token = result.get('access_token')
    expires_in = result.get('expires_in', 7200)
    if token:
        cache.set(_WECHAT_TOKEN_CACHE_KEY, token, max(60, int(expires_in) - 200))
        return token

    logger.error("获取access_token失败: errcode=%s", result.get('errcode'))
    return None
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/notice/services.py
git commit -m "perf(notice): cache wechat access_token to avoid daily quota exhaustion; redact secret from logs"
```

---

### Task 3.2: 配额扣减竞态 — 锁内条件更新 + token 过期重试一次

**问题**：`apps/notice/services.py:35-103` 锁提前释放、扣减在锁外、无 errcode 处理。改为原子条件扣减，40001 时刷新 token 重试一次。

**Files:**
- Modify: `apps/notice/services.py`（`send_template_msg` 函数）

- [ ] **Step 1: 重写 send_template_msg**

将 `send_template_msg`（原第 29-103 行，行号随 Task 3.1 改动而后移）整体替换为：

```python
def send_template_msg(user, template_id, page_path, data_dict):
    """发送订阅消息：原子扣减额度，发送失败则回补，token 过期重试一次"""
    if not user.wechat_openid:
        logger.warning("跳过推送: 用户 %s 无 wechat_openid", user.username)
        return False

    # 1. 原子条件扣减额度（immune to lost-update）
    rows = (
        UserQuota.objects
        .filter(user=user, template_id=template_id, count__gt=0)
        .update(count=F('count') - 1)
    )
    if rows == 0:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无可用订阅额度'
        )
        return False

    def _refund():
        UserQuota.objects.filter(user=user, template_id=template_id).update(count=F('count') + 1)

    # 2. 获取 token
    access_token = get_wechat_access_token()
    if not access_token:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无法获取access_token'
        )
        return False

    def _do_send(token):
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}"
        payload = {
            "touser": user.wechat_openid,
            "template_id": template_id,
            "page": page_path,
            "miniprogram_state": "formal",
            "lang": "zh_CN",
            "data": data_dict,
        }
        resp = requests.post(url, json=payload, timeout=5)
        return resp.json()

    # 3. 发送（token 失效 40001 时刷新重试一次）
    try:
        res_json = _do_send(access_token)
        if res_json.get('errcode') == 40001:
            access_token = get_wechat_access_token(force_refresh=True)
            if access_token:
                res_json = _do_send(access_token)
    except Exception as e:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=str(e)
        )
        logger.error("用户 %s 模板 %s 微信接口异常: %s", user.username, template_id, type(e).__name__)
        return False

    # 4. 处理结果
    if res_json.get('errcode') == 0:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='success', wechat_msg_id=res_json.get('msgid'), sent_at=timezone.now()
        )
        return True
    else:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=res_json.get('errmsg')
        )
        logger.error("用户 %s 模板 %s 推送失败: %s", user.username, template_id, res_json.get('errmsg'))
        return False
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/notice/services.py
git commit -m "fix(notice): atomic quota decrement with refund on failure and 40001 token retry"
```

---

### Task 3.3: 提醒任务只发有 openid 且该模板有额度的用户

**问题**：`apps/notice/tasks.py:73-76` 未排除无 openid 用户、未按 template_id 过滤额度。

**Files:**
- Modify: `apps/notice/tasks.py:56-76`

- [ ] **Step 1: 收紧查询集**

将第 73-76 行替换为：

```python
    users_to_remind = (
        User.objects
        .exclude(id__in=filled_user_ids)
        .exclude(wechat_openid__isnull=True)
        .exclude(wechat_openid__exact='')
        .filter(notice_quotas__template_id=template_id, notice_quotas__count__gt=0)
        .distinct()
    )
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/notice/tasks.py
git commit -m "fix(notice): only remind users with wechat_openid and quota for the target template"
```

---

### Task 3.4: 订阅同步竞态 — 直接 update 免除 lost-update

**问题**：`apps/notice/views.py:26-31` 先 get_or_create 再 F()+save，与并发扣减存在 lost-update。

**Files:**
- Modify: `apps/notice/views.py:1-37`

- [ ] **Step 1: 用无实例加载的原子 update**

将第 25-36 行替换为：

```python
    if action == 'accept':
        import logging
        logger = logging.getLogger("notice.views")
        UserQuota.objects.get_or_create(user=request.user, template_id=template_id)
        UserQuota.objects.filter(
            user=request.user, template_id=template_id
        ).update(count=F('count') + 1)
        quota = UserQuota.objects.get(user=request.user, template_id=template_id)
        logger.info(
            "用户 %s 模板 %s 订阅额度变更: 当前额度 %s",
            request.user.username, template_id, quota.count,
        )
        return SubscribeSyncResponseSchema(status="success", msg="订阅次数已增加")
```

- [ ] **Step 2: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 3: Commit**

```
git add apps/notice/views.py
git commit -m "fix(notice): atomic quota increment on subscribe to avoid lost updates"
```

---

# Phase 4 — 清理

### Task 4.1: 移除损坏的量表 YAML 导入死管线

**问题**：`load_scales_from_yaml.py` 导入不存在的 `ScaleConfig`、路径错误；entrypoint 检查错误目录导致静默跳过。运行时量表实际走 registry 插件。用户决策：移除死管线。

**Files:**
- Delete: `apps/scales/management/commands/load_scales_from_yaml.py`
- Modify: `docker-entrypoint.sh:67-71`
- Modify: `README.md`（量表条目描述）

- [ ] **Step 1: 删除损坏命令**

Run: `git rm apps/scales/management/commands/load_scales_from_yaml.py`

- [ ] **Step 2: 移除 entrypoint 中的调用**

将 `docker-entrypoint.sh` 第 67-71 行删除：
```bash
    # 4. 加载量表配置
    if [ -d "apps/scales/yaml_configs" ]; then
        echo "📊 Loading scale configurations from YAML..."
        uv run python manage.py load_scales_from_yaml
    fi
```

- [ ] **Step 3: 更新 README 量表描述**

将 `README.md` 第 15 行：
```
| 量表系统 | 插件化量表架构，支持 YAML 配置导入，已实现 GAD-7 |
```
改为：
```
| 量表系统 | 插件化量表架构（Python 定义类，registry 自动发现），已实现 GAD-7 |
```

同时将第 129 行：
```
- 量表配置：YAML 文件位于 `apps/scales/yaml_configs/`，启动时自动导入
```
改为：
```
- 量表配置：Python 定义类位于 `apps/scales/definitions/`，由 registry 在运行时自动发现
```

- [ ] **Step 4: 验证 entrypoint 语法**

Run: `bash -n docker-entrypoint.sh` （若无 bash，则跳过并人工核对）
Expected: 无语法错误

- [ ] **Step 5: Commit**

```
git add apps/scales/management/commands/load_scales_from_yaml.py docker-entrypoint.sh README.md
git commit -m "chore(scales): remove broken YAML import pipeline; registry is the single source of truth"
```

---

### Task 4.2: 管理端存储型 XSS — 用 format_html 参数化转义

**问题**：`apps/scales/admin.py:50-77`、`apps/reports/admin.py:58-79` 用 f-string 拼 HTML 后再 format_html，未转义用户 JSON。

**Files:**
- Modify: `apps/scales/admin.py:50-77`
- Modify: `apps/reports/admin.py:58-79`

- [ ] **Step 1: scales selected_options_display 转义**

将 `apps/scales/admin.py` 第 50-77 行的 `selected_options_display` 替换为：

```python
    def selected_options_display(self, obj):
        """选项选择显示（转义用户内容防 XSS）"""
        from django.utils.html import format_html, format_html_join, mark_safe
        if obj.selected_options:
            try:
                if isinstance(obj.selected_options, list):
                    rows = []
                    for i, option in enumerate(obj.selected_options, 1):
                        if isinstance(option, dict):
                            rows.append(format_html(
                                "<strong>{}:</strong> {}",
                                option.get('question', f'问题 {i}'),
                                option.get('answer', ''),
                            ))
                        else:
                            rows.append(format_html("{}. {}", i, option))
                    return mark_safe("<br>".join(str(r) for r in rows))
                else:
                    formatted = json.dumps(obj.selected_options, ensure_ascii=False, indent=2)
                    return format_html(
                        '<pre style="background: #f8f9fa; padding: 10px; '
                        'border: 1px solid #dee2e6; border-radius: 4px;">{}</pre>',
                        formatted,
                    )
            except Exception:
                return "数据格式错误"
        return "无选项数据"

    selected_options_display.short_description = '选项选择'
```

> 注意：删除 `selected_options_display.allow_tags = True`（已废弃属性）。`format_html` 的每个 `{}` 会自动 HTML 转义，`<script>` 变为惰性文本。

- [ ] **Step 2: reports recommendations_display 转义**

将 `apps/reports/admin.py` 第 58-79 行的 `recommendations_display` 替换为：

```python
    def recommendations_display(self, obj):
        """建议列表显示（转义用户内容防 XSS）"""
        from django.utils.html import format_html, mark_safe
        if obj.recommendations:
            try:
                if isinstance(obj.recommendations, list):
                    rows = []
                    for i, rec in enumerate(obj.recommendations, 1):
                        if isinstance(rec, dict):
                            rows.append(format_html(
                                "<strong>{}:</strong> {}",
                                rec.get('title', f'建议 {i}'),
                                rec.get('content', ''),
                            ))
                        else:
                            rows.append(format_html("{}. {}", i, rec))
                    return mark_safe("<br>".join(str(r) for r in rows))
                else:
                    return str(obj.recommendations)
            except Exception:
                return "格式错误"
        return "无建议"

    recommendations_display.short_description = '建议列表'
```

> 删除 `recommendations_display.allow_tags = True`。

- [ ] **Step 3: 验证**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues

- [ ] **Step 4: Commit**

```
git add apps/scales/admin.py apps/reports/admin.py
git commit -m "fix(admin): escape user JSON in display fields to prevent stored XSS"
```

---

### Task 4.3: 修复 scales/models.py 中文乱码 verbose_name

**问题**：`apps/scales/models.py:9` `started_at` 的 verbose_name 为损坏编码 `"开始时�?"`。

**Files:**
- Modify: `apps/scales/models.py:9`

- [ ] **Step 1: 修正 verbose_name**

将第 9 行：
```python
    started_at = models.DateTimeField(verbose_name="开始时�?)
```
改为：
```python
    started_at = models.DateTimeField(verbose_name="开始时间")
```

- [ ] **Step 2: 生成迁移（仅 verbose_name 变更，无 schema 影响）**

Run: `uv run python manage.py makemigrations scales --settings=config.settings_test`
Expected: 生成一个 alter verbose_name 的迁移

- [ ] **Step 3: 验证迁移可应用**

Run: `uv run python manage.py migrate --settings=config.settings_test`
Expected: OK

- [ ] **Step 4: Commit**

```
git add apps/scales/models.py apps/scales/migrations/
git commit -m "fix(scales): repair corrupted verbose_name encoding on started_at"
```

---

### Task 4.4: 清理未使用导入（ruff F401）

**问题**：6 处 F401（cognitive_flow/journals/reports/scales admin + admin_mixins）。

**Files:**
- Modify: `apps/cognitive_flow/admin.py:3`
- Modify: `apps/journals/admin.py:3`
- Modify: `apps/reports/admin.py:4`
- Modify: `apps/scales/admin.py:4`
- Modify: `apps/users/admin_mixins.py:4`

- [ ] **Step 1: 用 ruff 自动修复**

Run: `uv run ruff check . --fix`
Expected: `Found 6 errors (6 fixed, 0 remaining)` 或类似

> 注意：Task 4.2 已在 scales/reports admin 内部函数中局部 `import format_html`，故顶部 F401 可安全移除；若 ruff 误删仍被使用的导入，回退该文件手动处理。

- [ ] **Step 2: 复核无残留**

Run: `uv run ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: 运行全量测试确保无破坏**

Run: `uv run python manage.py test --settings=config.settings_test`
Expected: OK

- [ ] **Step 4: Commit**

```
git add apps/cognitive_flow/admin.py apps/journals/admin.py apps/reports/admin.py apps/scales/admin.py apps/users/admin_mixins.py
git commit -m "chore: remove unused imports flagged by ruff (F401)"
```

---

### Task 4.5: setup_periodic_tasks 幂等性收敛（按 name 更新）

**问题**：`setup_periodic_tasks.py:27,64` 用 crontab+name 双键 get_or_create，改时间会撞 name 唯一约束。改为按 name 定位、更新 crontab。

**Files:**
- Modify: `apps/notice/management/commands/setup_periodic_tasks.py:27-88`

- [ ] **Step 1: 抽取 upsert 辅助并按 name 更新**

将 `handle` 方法中两处任务创建（第 27-52 与 64-88 行）替换为统一逻辑。整段 `handle` 主体（第 14 行 def 之后）替换为：

```python
    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()

        def upsert(name, hour, kwargs, description):
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute="0", hour=str(hour), day_of_week="*",
                day_of_month="*", month_of_year="*", timezone=tz,
            )
            task, created = PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    "crontab": schedule,
                    "task": "apps.notice.tasks.send_mood_reminder",
                    "kwargs": json.dumps(kwargs),
                    "enabled": True,
                    "description": description,
                },
            )
            verb = "已创建" if created else "已更新"
            self.stdout.write(self.style.SUCCESS(f"✅ {name} 定时任务{verb}"))

        upsert("早上情绪测评提醒", 9, {"period": "morning"}, "每天早上 9:00 提醒用户进行早间情绪测评")
        upsert("晚上情绪测评提醒", 21, {"period": "evening"}, "每天晚上 21:00 提醒用户进行晚间情绪测评")
        self.stdout.write(self.style.SUCCESS("🎉 定时任务设置完成！"))
```

- [ ] **Step 2: 验证命令可运行**

Run: `uv run python manage.py setup_periodic_tasks --settings=config.settings_test`
Expected: 输出“已创建”，再次运行输出“已更新”，无 IntegrityError

- [ ] **Step 3: Commit**

```
git add apps/notice/management/commands/setup_periodic_tasks.py
git commit -m "fix(notice): make periodic task setup idempotent by name via update_or_create"
```

---

### Task 4.6: SECURE_PROXY_SSL_HEADER 去重（仅保留 DEBUG 外声明）

**问题**：`config/settings.py:149` 无条件设置，`:328` 已在 `if not DEBUG` 内重复。DEBUG 下可被伪造。

**Files:**
- Modify: `config/settings.py:148-149`

- [ ] **Step 1: 删除模块级无条件声明**

删除第 148-149 行：
```python
# 代理配置：告知 Django 它正运行在 Nginx 后面，需要基于 X-Forwarded-Proto 头判断 HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```
（保留 `if not DEBUG:` 块内第 328 行的声明。）

- [ ] **Step 2: 验证生产配置仍生效**

Run: `uv run python -c "import os; os.environ['JWT_SIGNING_KEY']='x'; os.environ['DEBUG']='False'; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); django.setup(); from django.conf import settings; print(settings.SECURE_PROXY_SSL_HEADER)"`
Expected: `('HTTP_X_FORWARDED_PROTO', 'https')`

- [ ] **Step 3: Commit**

```
git add config/settings.py
git commit -m "fix(settings): only trust X-Forwarded-Proto in production (remove unconditional header)"
```

---

### Task 4.7: SECRET_KEY 生产 fail-fast（对齐 JWT_SIGNING_KEY 模式，保留 DEBUG 回退）

**问题**：`config/settings.py:30-33` 硬编码不安全 SECRET_KEY 回退，生产缺失时静默启用。对齐已有 JWT fail-fast 写法：DEBUG 下仍回退（不破坏本地/CI 可用性），生产缺失才报错。

**Files:**
- Modify: `config/settings.py:29-37`

- [ ] **Step 1: 生产缺失即 fail-fast，DEBUG 保留开发默认**

将第 29-37 行替换为：

```python
# 调试模式（先解析 DEBUG，供 SECRET_KEY 判定使用）
# 默认为 False (生产环境安全优先)，仅在明确设置环境变量为 True 时开启
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# 安全密钥
# 生产(DEBUG=False)必须由环境变量提供，缺失即启动失败(fail-fast)，
# 避免静默回落到源码中的不安全默认值。DEBUG 下保留开发默认以不阻断本地/CI。
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-b2#f(%-90xf8y7$54+l50r_p!eyfxd0xw2qu+uok+(z&_jc*px'
    else:
        raise RuntimeError(
            "SECRET_KEY 未设置。生产环境必须通过环境变量提供该密钥。"
        )
```

> 注意：本改动把原第 37 行的 `DEBUG = ...` 上移到 SECRET_KEY 之前。确认后续第 40 行起对 `DEBUG` 的使用不受影响（仅顺序变化）。原第 35-37 行的 `DEBUG` 定义需删除以免重复。

- [ ] **Step 2: 删除原重复的 DEBUG 定义**

确认第 35-37 行（原 `# 调试模式 ... DEBUG = ...`）已被 Step 1 合并，不得残留第二处 `DEBUG =` 赋值。

- [ ] **Step 3: 验证 DEBUG 下可正常导入**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: no issues（settings_test 继承 settings，DEBUG=False 但显式提供了 JWT_SIGNING_KEY；SECRET_KEY 在 test 环境由继承的 os.environ 决定——若 CI 无 SECRET_KEY 且 DEBUG=False 会 fail-fast）

- [ ] **Step 4: 为测试配置补 SECRET_KEY，保 settings_test 可用（可用性优先）**

在 `config/settings_test.py` 第 6 行 `os.environ.setdefault("JWT_SIGNING_KEY", ...)` 之后追加一行：

```python
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-for-production")
```

- [ ] **Step 5: 复跑测试确认不受影响**

Run: `uv run python manage.py test --settings=config.settings_test`
Expected: OK

- [ ] **Step 6: Commit**

```
git add config/settings.py config/settings_test.py
git commit -m "fix(settings): fail-fast on missing SECRET_KEY in production, keep DEBUG dev fallback"
```

---

# 最终验收

### Task 5.1: 全量回归

- [ ] **Step 1: 系统检查**

Run: `uv run python manage.py check --settings=config.settings_test`
Expected: `System check identified no issues`

- [ ] **Step 2: 迁移漂移检查（业务 app）**

Run: `uv run python manage.py makemigrations --check --dry-run apps.users apps.articles apps.journals apps.reports apps.scales apps.notice apps.emotiontracker apps.feedback apps.cognitive_flow --settings=config.settings_test`
Expected: 退出码 0

- [ ] **Step 3: 全量测试**

Run: `uv run python manage.py test --settings=config.settings_test`
Expected: 全部 PASS（含新增测试）

- [ ] **Step 4: Lint**

Run: `uv run ruff check .`
Expected: `All checks passed!`

- [ ] **Step 5: 生产 settings 冒烟（fail-fast 生效）**

Run: `uv run python manage.py check --deploy --settings=config.settings 2>&1`（本地无 JWT_SIGNING_KEY 时应 fail-fast，属预期）
Expected: 观察输出无异常回退

---

## 变更影响与回滚

- 所有改动为源码级、可用 `git revert <commit>` 单条回滚。
- 唯一 DB 迁移为 Task 4.3（`scales` verbose_name，无 schema/数据影响）。
- 无新增依赖、无容器/资源画像变更、无 Celery/Gunicorn 并发参数变更。
- 认证加固均已核实与小程序当前请求兼容（携带 Bearer / 不调用写接口）。
