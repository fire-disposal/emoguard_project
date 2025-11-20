# Docker Compose 配置使用说明

## 概述

通过使用 Docker Compose 的 override 功能，我们可以将生产配置和本地调试配置分离，避免代码重复，使配置更加简洁和易于维护。

## 文件结构

- `docker-compose.yml` - 基础配置文件（生产环境配置）
- `docker-compose.override.yml` - 本地开发覆盖配置（自动加载）
- `docker-compose.local.yml` - 旧的本地配置文件（已废弃）

## 使用方法

### 本地开发环境

在本地开发时，Docker Compose 会自动加载 `docker-compose.yml` 和 `docker-compose.override.yml` 两个文件：

```bash
# 启动所有服务（自动加载 override 文件）
docker-compose up -d

# 或者显式指定
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 生产环境

在生产环境中，只使用基础配置文件：

```bash
# 生产环境启动（不加载 override 文件）
docker-compose -f docker-compose.yml up -d
```

## 配置对比

### 主要优化点

1. **代码量减少**：从 109 行减少到 26 行，减少了 76% 的代码量
2. **避免重复**：不再需要维护两份几乎相同的配置
3. **易于维护**：本地特有的配置集中在 override 文件中

### 具体差异

| 配置项 | 基础配置 (docker-compose.yml) | 覆盖配置 (docker-compose.override.yml) |
|--------|------------------------------|--------------------------------------|
| 镜像构建 | 使用预构建镜像 (`image: ghcr.io/...`) | 本地构建 (`build: .`) |
| 代码挂载 | 生产路径 (`/srv/emoguard/...`) | 本地路径 (`./...`) |
| 数据卷 | 生产路径 (`/srv/emoguard/...`) | 本地路径 (`./...`) |

## 迁移步骤

1. **备份旧的本地配置**：
   ```bash
   cp docker-compose.local.yml docker-compose.local.yml.backup
   ```

2. **使用新的 override 配置**：
   ```bash
   # 直接启动即可，会自动加载 override 文件
   docker-compose up -d
   ```

3. **验证服务状态**：
   ```bash
   docker-compose ps
   docker-compose logs
   ```

4. **删除旧的配置文件**（确认新配置工作正常后）：
   ```bash
   rm docker-compose.local.yml
   ```

## 优势

1. **DRY 原则**：Don't Repeat Yourself，避免配置重复
2. **自动加载**：override 文件会自动被 Docker Compose 识别和加载
3. **环境隔离**：生产和开发环境配置完全分离
4. **易于理解**：配置结构更清晰，维护成本更低

## 注意事项

- 确保 `.pgdata` 和 `.redisdata` 目录有适当的权限
- 本地开发时，代码变更会自动生效（因为挂载了当前目录）
- 生产环境不会意外加载开发配置