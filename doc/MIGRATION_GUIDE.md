# 数据库迁移指南

本文档说明如何执行系统精简重构后的数据库迁移。

## 重要提示

**在执行迁移前，请务必备份数据库！**

## 迁移步骤

### 1. 备份数据库

```bash
# 如果使用SQLite
cp db.sqlite3 db.sqlite3.backup

# 如果使用PostgreSQL
pg_dump your_database > backup.sql
```

### 2. 创建迁移文件

```bash
python manage.py makemigrations
```

### 3. 查看迁移计划

```bash
python manage.py showmigrations
```

### 4. 执行迁移

```bash
python manage.py migrate
```

## 模型变更说明

### User模型变更

**移除的字段：**
- `avatar` (URLField) - 头像URL字段
- `bio` (TextField) - 个人简介字段
- `education` (CharField) - 学历字段
- `occupation` (CharField) - 职业字段
- `EDUCATION_CHOICES` - 学历选项枚举

**保留的字段：**
- 基础认证字段（username, password, email等）
- 微信字段（wechat_openid, wechat_unionid）
- 角色字段（role）
- 基础资料（nickname, real_name, gender, birthday）
- 联系信息（phone, address）

### Article模型变更

**修改的字段：**
- `cover_image`: CharField → ImageField
  - 从存储URL改为实际文件上传
  - 上传路径: `media/articles/covers/{year}/{month}/`

**新增索引：**
- publish_time（降序）
- status

### MoodJournal模型变更

**移除的字段：**
- `mood_name` (CharField) - 情绪名称
- `mood_emoji` (CharField) - 情绪表情

**修改的字段：**
- `text`: CharField(max_length=512) → TextField(max_length=1000)
  - 增加字段长度，支持更详细的内容

**新增索引：**
- (user, -record_date)
- -created_at

### 新增Notification模型

**字段说明：**
- `user`: 接收用户（外键到User）
- `title`: 通知标题
- `content`: 通知内容
- `notification_type`: 通知类型（system/assessment/reminder）
- `is_read`: 是否已读
- `related_id`: 关联对象ID（可选）
- `related_type`: 关联对象类型（可选）
- `created_at`: 创建时间
- `read_at`: 阅读时间（可选）

**索引：**
- (user, is_read)
- (user, -created_at)
- -created_at

## 数据迁移注意事项

### 1. User模型数据迁移

移除的字段数据将丢失，如需保留：

```python
# 在迁移前导出数据
from apps.users.models import User
import json

users_data = []
for user in User.objects.all():
    users_data.append({
        'id': str(user.id),
        'avatar': user.avatar,
        'bio': user.bio,
        'education': user.education,
        'occupation': user.occupation
    })

with open('user_archived_data.json', 'w') as f:
    json.dump(users_data, f, ensure_ascii=False, indent=2)
```

### 2. Article模型数据迁移

cover_image从URL转为文件字段：

```python
# 迁移前需要手动处理图片
# 选项1: 将现有URL图片下载到本地
# 选项2: 清空cover_image字段，重新上传
```

### 3. MoodJournal模型数据迁移

移除的mood_name和mood_emoji字段：
- 这些字段的信息将丢失
- 主要数据（mood_score和text）会保留

## 迁移后验证

### 1. 检查迁移状态

```bash
python manage.py showmigrations
```

所有应用的迁移应显示为已应用 [X]。

### 2. 验证数据完整性

```bash
python manage.py shell
```

```python
# 检查User模型
from apps.users.models import User
print(f"用户总数: {User.objects.count()}")

# 检查Notification模型
from apps.notifications.models import Notification
print(f"通知总数: {Notification.objects.count()}")

# 检查MoodJournal模型
from apps.journals.models import MoodJournal
print(f"日记总数: {MoodJournal.objects.count()}")
```

### 3. 测试API功能

```bash
python manage.py runserver
```

访问 http://localhost:8000/api/docs 测试各个API端点。

## 回滚方案

如果迁移出现问题，可以回滚：

```bash
# 恢复数据库备份
# SQLite
rm db.sqlite3
cp db.sqlite3.backup db.sqlite3

# PostgreSQL
psql your_database < backup.sql
```

## 常见问题

### Q1: 迁移失败，提示字段冲突

**解决方案：**
1. 删除所有迁移文件（保留__init__.py）
2. 删除数据库
3. 重新创建迁移
4. 重新执行迁移

### Q2: ImageField需要Pillow库

**解决方案：**
```bash
pip install Pillow
```

### Q3: 数据丢失

**预防措施：**
- 始终在迁移前备份数据库
- 在测试环境先执行迁移
- 验证迁移结果后再应用到生产环境

## 生产环境部署建议

1. **停机维护**
   - 通知用户系统维护时间
   - 停止应用服务器

2. **备份验证**
   - 完整备份数据库
   - 验证备份可恢复性

3. **执行迁移**
   - 在生产环境执行迁移
   - 监控迁移日志

4. **验证测试**
   - 验证关键功能
   - 检查数据完整性

5. **启动服务**
   - 启动应用服务器
   - 监控系统运行状态

6. **监控观察**
   - 观察系统运行24小时
   - 准备回滚方案
