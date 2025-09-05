# 🪄 Magic 魔法初始化指南

## 一键生成完整微服务

`magic` 命令让你只需一行代码就能创建包含所有功能的完整微服务！

## 🚀 快速开始

### 基础用法
```bash
# 在当前目录创建魔法微服务
micro-gen magic --name my-awesome-service

# 指定路径和名称
micro-gen magic --path ./projects --name full-stack-service

# 使用配置文件
micro-gen magic --config ./examples/magic-config.yaml --name enterprise-service
```

### 完整参数
```bash
micro-gen magic [OPTIONS]

选项:
  --path TEXT    项目路径 (默认: 当前目录)
  --name TEXT    项目名称 (默认: magic-service)
  --config TEXT  配置文件路径 (可选)
  --force        强制覆盖现有文件
  --help         显示帮助信息
```

## 🎯 生成的功能

魔法初始化会自动集成以下所有功能：

| 功能 | 描述 | 技术栈 |
|---|---|---|
| **项目结构** | 整洁架构 + Go官方实践 | Go 1.21+ |
| **ES事件系统** | 事件溯源 + CQRS | NATS JetStream |
| **会话管理** | 分布式会话存储 | Redis + Memory |
| **任务系统** | 异步任务调度 | 内置调度器 |
| **Saga事务** | 分布式事务管理 | Saga模式 |
| **投影机制** | CQRS读模型 | 实时投影更新 |
| **Docker部署** | 生产就绪的容器化 | Docker + Compose |
| **Kubernetes部署** | 云原生部署清单 | K8s YAML |
| **CI/CD流水线** | GitHub Actions自动化 | GitHub Actions |
| **监控告警** | Prometheus + Grafana | 监控栈 |
| **一键部署脚本** | Makefile快捷命令 | Make

## 📋 使用示例

### 1. 创建标准微服务
```bash
mkdir my-service && cd my-service
micro-gen magic --name my-service
```

### 2. 使用配置文件
创建 `config.yaml`:
```yaml
project:
  name: "user-service"
  description: "用户管理服务"

event_sourcing:
  nats:
    url: "nats://localhost:4222"

session:
  redis:
    addr: "localhost:6379"
```

然后运行：
```bash
micro-gen magic --config config.yaml --name user-service
```

### 3. 强制重新生成
```bash
micro-gen magic --force --name fresh-service
```

### 一键部署
```bash
# 生成部署配置
micro-gen deploy --name my-service

# 启动服务
make deploy-local

# 访问应用
open http://localhost:8080
```

## 🔧 项目结构

执行后生成的目录结构：

```
my-service/
├── cmd/api/
│   └── main.go
├── internal/
│   ├── entity/
│   ├── usecase/
│   │   ├── event/
│   │   ├── session/
│   │   ├── task/
│   │   ├── saga/
│   │   └── projection/
├── pkg/
│   ├── config/
│   ├── event/
│   ├── session/
│   ├── task/
│   ├── saga/
│   └── projection/
├── adapter/
│   ├── handler/
│   └── repo/
├── data/snapshots/
├── go.mod
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚦 启动步骤

生成项目后：

```bash
cd your-project

# 1. 安装依赖
go mod tidy

# 2. 启动基础设施
docker-compose up -d

# 3. 运行服务
go run cmd/api/main.go
```

## 🎨 配置文件示例

查看 `examples/magic-config.yaml` 获取完整配置示例。

## ✨ 特性亮点

- **零配置启动**：默认配置即可运行
- **生产就绪**：包含Docker、监控、日志
- **可扩展**：基于整洁架构，易于扩展
- **文档齐全**：每个模块都有详细文档
- **测试覆盖**：包含完整的测试用例

## 🎪 一句话总结

> 一行命令，一个完整的微服务帝国！

```bash
micro-gen magic --name my-empire
```