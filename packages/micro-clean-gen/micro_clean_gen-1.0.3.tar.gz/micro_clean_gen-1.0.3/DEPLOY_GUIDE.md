# 🚀 一键部署指南

## 项目简介

本项目提供了**一键生成完整部署配置**的能力，包含从本地开发到生产部署的全套方案。

## 🎯 快速开始

### 1. 生成部署配置
```bash
# 在项目目录中执行
micro-gen deploy --name my-service

# 或指定路径
micro-gen deploy --path ./my-project --name awesome-service
```

### 2. 本地开发部署
```bash
# 启动所有服务（应用 + 数据库 + 消息队列 + 监控）
make deploy-local

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 3. 访问服务
- **应用**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 📁 部署结构

```
deploy/
├── docker-compose.yml      # 本地开发环境
├── prometheus.yml          # 监控配置
├── k8s/                   # Kubernetes部署
│   ├── deployment.yml     # 应用部署
│   └── service.yml        # 服务暴露
├── README.md              # 部署文档

.github/
└── workflows/
    └── deploy.yml         # CI/CD流水线

Makefile                   # 快捷命令
Dockerfile                # 生产镜像
.dockerignore            # Docker忽略文件
```

## 🛠️ 部署组件

### 应用服务
- **Go微服务**: 基于整洁架构的生产应用
- **健康检查**: 内置健康检查端点
- **优雅关闭**: 支持优雅重启和关闭

### 基础设施
- **NATS**: 消息队列和事件总线
- **Redis**: 缓存和会话存储
- **PostgreSQL**: 主数据库
- **Prometheus**: 指标收集
- **Grafana**: 可视化监控

### 开发工具
- **Docker Compose**: 本地开发环境
- **Makefile**: 快捷命令
- **GitHub Actions**: CI/CD流水线

## 🔧 常用命令

### 本地开发
```bash
# 启动所有服务
make deploy-local

# 停止服务
make stop

# 查看日志
make logs

# 清理环境
make clean

# 重新构建并启动
make rebuild
```

### 生产部署
```bash
# 构建镜像
docker build -t my-service:latest .

# Kubernetes部署
kubectl apply -f deploy/k8s/

# 检查部署状态
kubectl get pods -l app=my-service
```

### 监控运维
```bash
# 查看Prometheus指标
curl http://localhost:8080/metrics

# 查看Grafana仪表板
open http://localhost:3000

# 查看服务健康状态
curl http://localhost:8080/health
```

## 🌐 环境配置

### 环境变量
```bash
# 应用配置
APP_ENV=production
PORT=8080

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=magic_service
POSTGRES_USER=magic_user
POSTGRES_PASSWORD=magic_pass

# Redis配置
REDIS_ADDR=redis:6379
REDIS_PASSWORD=
REDIS_DB=0

# NATS配置
NATS_URL=nats://nats:4222
```

### 配置文件
```yaml
# docker-compose.yml 示例
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=production
    depends_on:
      - postgres
      - redis
      - nats
    restart: unless-stopped
```

## 📊 监控指标

### 内置指标
- **HTTP请求**: 请求次数、延迟、错误率
- **业务指标**: 自定义业务逻辑指标
- **系统指标**: CPU、内存、GC等

### 自定义指标
```go
// 添加自定义指标
var requestCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "myapp_requests_total",
        Help: "Total number of requests",
    },
    []string{"method", "endpoint"},
)
```

## 🚀 CI/CD流水线

### GitHub Actions
- **自动构建**: 推送到main分支自动触发
- **测试**: 运行单元测试和集成测试
- **镜像**: 构建并推送Docker镜像
- **部署**: 自动部署到测试环境

### 工作流文件
```yaml
# .github/workflows/deploy.yml
name: Build and Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go build -v ./...
      - run: go test -v ./...
      - run: docker build -t ${{ github.repository }}:latest .
```

## 🔒 安全最佳实践

### 容器安全
- **非root用户**: 使用非root用户运行容器
- **最小权限**: 只暴露必要端口
- **健康检查**: 内置健康检查端点

### 数据安全
- **密码加密**: 使用环境变量管理敏感信息
- **网络隔离**: 使用Docker网络隔离服务
- **定期更新**: 定期更新基础镜像

## 📈 性能优化

### 镜像优化
- **多阶段构建**: 减小最终镜像大小
- **缓存利用**: 优化Dockerfile缓存层
- **基础镜像**: 使用Alpine最小化镜像

### 资源限制
```yaml
# Kubernetes资源限制
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

## 🎯 下一步

1. **自定义配置**: 根据业务需求调整配置
2. **扩展服务**: 添加更多微服务
3. **监控告警**: 配置告警规则
4. **日志聚合**: 集成ELK日志系统
5. **服务网格**: 考虑使用Istio等服务网格

## 🆘 故障排除

### 常见问题
```bash
# 端口冲突
lsof -i :8080

# 查看容器日志
docker-compose logs app

# 清理Docker缓存
docker system prune -f

# 重新拉取镜像
docker-compose pull
```

### 调试技巧
- 使用 `docker-compose logs -f` 实时查看日志
- 使用 `kubectl describe pod` 查看K8s Pod详情
- 使用 `curl` 测试健康检查端点