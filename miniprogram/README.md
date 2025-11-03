# 认知照顾情绪监测系统 - 微信原生小程序

基于微信原生小程序开发的情绪监测与心理健康管理系统。

## 项目说明

本项目是对原 uniapp 项目的微信原生小程序重构版本，完全使用微信小程序原生 API 实现，不依赖任何第三方框架。

## 目录结构

```
native-miniprogram/
├── pages/                      # 页面目录
│   ├── login/                  # 登录页
│   ├── index/                  # 首页
│   ├── mood/record/            # 情绪记录
│   ├── articles/               # 文章
│   │   ├── list/               # 文章列表
│   │   └── detail/             # 文章详情
│   ├── assessment/             # 测评
│   │   ├── select/             # 选择量表
│   │   ├── detail/             # 量表答题
│   │   └── result/             # 测评结果
│   ├── reports/                # 报告
│   │   ├── list/               # 报告列表
│   │   └── detail/             # 报告详情
│   └── profile/index/          # 个人中心
├── utils/                      # 工具函数
│   ├── request.js              # 网络请求封装
│   ├── auth.js                 # 鉴权工具
│   └── storage.js              # 本地存储封装
├── api/                        # API 接口定义
│   ├── user.js                 # 用户相关
│   ├── journal.js              # 情绪日记
│   ├── article.js              # 文章
│   ├── scale.js                # 量表
│   └── report.js               # 报告
├── app.js                      # 小程序入口
├── app.json                    # 全局配置
├── app.wxss                    # 全局样式
└── project.config.json         # 项目配置
```

## 核心功能

### 已实现功能

1. **用户登录**
   - 微信小程序授权登录
   - Token 自动刷新
   - 登录状态持久化

2. **首页**
   - 显示当前时间和日期
   - 功能快捷入口
   - 主要功能卡片导航

3. **情绪记录**
   - 6种情绪选择（非常开心、开心、一般、难过、很难过、焦虑）
   - 文本输入记录原因
   - 历史记录查看

4. **工具函数**
   - request.js: 网络请求封装，支持自动添加 Token、错误处理、Token 刷新
   - auth.js: 鉴权工具，管理登录状态和用户信息
   - storage.js: 本地存储封装

5. **API 接口**
   - user.js: 用户相关接口
   - journal.js: 情绪日记接口
   - article.js: 文章接口
   - scale.js: 量表接口
   - report.js: 报告接口

### 待完善功能

以下页面需要创建对应的 wxml、wxss、json 文件：

- `pages/mood/record/` - 情绪记录页面视图
- `pages/articles/list/` - 文章列表
- `pages/articles/detail/` - 文章详情
- `pages/assessment/select/` - 量表选择
- `pages/assessment/detail/` - 量表答题
- `pages/assessment/result/` - 测评结果
- `pages/reports/list/` - 报告列表
- `pages/reports/detail/` - 报告详情
- `pages/profile/index/` - 个人中心

## 开发指南

### 环境要求

- 微信开发者工具
- 微信小程序 AppID（可使用测试号）

### 配置说明

1. **修改 API 基础地址**

编辑 `utils/request.js`，修改 `BASE_URL` 为实际后端地址：

```javascript
const BASE_URL = 'http://127.0.0.1:8000';  // 修改为实际地址
```

2. **配置小程序 AppID**

编辑 `project.config.json`，修改 `appid` 字段：

```json
{
  "appid": "your-appid-here"
}
```

3. **配置合法域名**

在微信小程序后台配置服务器域名（开发阶段可在开发者工具中关闭域名校验）。

### 开发流程

1. 使用微信开发者工具打开 `native-miniprogram` 目录
2. 编译运行，查看效果
3. 根据需要完善各页面功能

### 页面开发规范

每个页面由 4 个文件组成：

- `.wxml` - 页面结构
- `.wxss` - 页面样式
- `.js` - 页面逻辑
- `.json` - 页面配置

示例（以情绪记录页面为例）：

```
pages/mood/record/
├── record.wxml   # 页面结构
├── record.wxss   # 页面样式
├── record.js     # 页面逻辑（已创建）
└── record.json   # 页面配置
```

## API 接口说明

所有接口调用严格遵循 `openapi.json` 定义，接口基础地址配置在 `utils/request.js` 中。

### 主要接口

**用户相关**
- POST `/api/users/wechat/login` - 微信登录
- GET `/api/users/me` - 获取当前用户信息
- PUT `/api/users/me/profile` - 更新用户资料

**情绪日记**
- GET `/api/journals/` - 获取日记列表
- POST `/api/journals/` - 创建日记
- GET `/api/journals/{journal_id}` - 获取日记详情
- PUT `/api/journals/{journal_id}` - 更新日记
- DELETE `/api/journals/{journal_id}` - 删除日记

**文章**
- GET `/api/articles/` - 获取文章列表
- GET `/api/articles/{article_id}` - 获取文章详情

**量表**
- GET `/api/scales/configs` - 获取量表配置列表
- GET `/api/scales/configs/{config_id}` - 获取量表详情
- POST `/api/scales/results` - 提交量表结果
- GET `/api/scales/results` - 获取测评结果列表
- GET `/api/scales/results/{result_id}` - 获取测评结果详情

**健康报告**
- GET `/api/reports/` - 获取报告列表
- GET `/api/reports/{report_id}` - 获取报告详情
- GET `/api/reports/summary/{user_id}` - 获取报告摘要
- GET `/api/reports/trends/{user_id}` - 获取健康趋势

## 注意事项

1. **域名配置**：需要在微信小程序后台配置合法的服务器域名
2. **HTTPS要求**：生产环境必须使用 HTTPS
3. **权限申请**：需要在 `app.json` 中声明所需权限
4. **包大小限制**：主包不超过 2MB，单个分包不超过 2MB

## 开发状态

### 已完成
- ✅ 项目基础架构
- ✅ 工具函数（request、auth、storage）
- ✅ API 接口封装
- ✅ 登录页面
- ✅ 首页
- ✅ 情绪记录页面逻辑

### 进行中
- 🔄 各页面视图文件创建
- 🔄 样式优化

### 待开发
- ⏳ 文章列表与详情页
- ⏳ 量表选择与答题页
- ⏳ 测评结果页
- ⏳ 健康报告列表与详情页
- ⏳ 个人中心页

## 技术特点

1. **纯原生实现**：不依赖任何第三方框架，代码简洁高效
2. **自动 Token 管理**：自动刷新过期 Token，无缝用户体验
3. **错误处理完善**：统一的错误处理和用户提示
4. **代码规范**：遵循微信小程序最佳实践
5. **接口严格对齐**：所有接口调用严格按照 openapi.json 定义

## 后续优化方向

1. 添加下拉刷新和上拉加载
2. 图片懒加载优化
3. 请求防抖和节流
4. 骨架屏加载效果
5. 错误边界处理
6. 数据缓存策略

## 许可证

本项目与原 uniapp 项目共享相同的许可证。
