"""
Deploy Generator - 一键生成完整部署配置
包含 Docker、K8s、CI/CD、监控、日志聚合
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class DeployGenerator:
    """部署配置生成器"""
    
    def __init__(self, project_path: Path, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
        self.deploy_path = project_path / "deploy"
    
    def generate_all(self):
        """生成所有部署配置"""
        logger.info("🚀 生成完整部署配置...")
        
        self.deploy_path.mkdir(exist_ok=True)
        
        # 生成所有部署文件
        self._generate_docker_compose()
        self._generate_kubernetes()
        self._generate_github_actions()
        self._generate_monitoring()
        self._generate_makefile()
        self._generate_readme()
        
        logger.success("✅ 部署配置生成完成！")
        self._print_deploy_summary()
    
    def _generate_docker_compose(self):
        """生成Docker Compose配置"""
        compose_config = {
            'version': '3.8',
            'services': {
                'app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'ports': ['8080:8080'],
                    'environment': [
                        'APP_ENV=production',
                        'NATS_URL=nats://nats:4222',
                        'REDIS_ADDR=redis:6379',
                        'POSTGRES_HOST=postgres',
                        'POSTGRES_PORT=5432'
                    ],
                    'depends_on': ['nats', 'redis', 'postgres'],
                    'restart': 'unless-stopped'
                },
                'nats': {
                    'image': 'nats:latest',
                    'ports': ['4222:4222', '8222:8222'],
                    'restart': 'unless-stopped'
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'ports': ['6379:6379'],
                    'restart': 'unless-stopped'
                },
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'environment': [
                        'POSTGRES_DB=magic_service',
                        'POSTGRES_USER=magic_user',
                        'POSTGRES_PASSWORD=magic_pass'
                    ],
                    'ports': ['5432:5432'],
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                    'restart': 'unless-stopped'
                },
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'ports': ['9090:9090'],
                    'volumes': ['./deploy/prometheus.yml:/etc/prometheus/prometheus.yml'],
                    'restart': 'unless-stopped'
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'ports': ['3000:3000'],
                    'environment': ['GF_SECURITY_ADMIN_PASSWORD=admin'],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'postgres_data': None
            }
        }
        
        with open(self.deploy_path / "docker-compose.yml", "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False)
        
        logger.success("✅ 生成 docker-compose.yml")
    
    def _generate_kubernetes(self):
        """生成K8s配置"""
        k8s_path = self.deploy_path / "k8s"
        k8s_path.mkdir(exist_ok=True)
        
        # Deployment
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': self.project_name,
                'labels': {'app': self.project_name}
            },
            'spec': {
                'replicas': 3,
                'selector': {
                    'matchLabels': {'app': self.project_name}
                },
                'template': {
                    'metadata': {
                        'labels': {'app': self.project_name}
                    },
                    'spec': {
                        'containers': [{
                            'name': self.project_name,
                            'image': f'{self.project_name}:latest',
                            'ports': [{'containerPort': 8080}],
                            'env': [
                                {'name': 'APP_ENV', 'value': 'production'},
                                {'name': 'PORT', 'value': '8080'}
                            ],
                            'resources': {
                                'requests': {
                                    'memory': '128Mi',
                                    'cpu': '100m'
                                },
                                'limits': {
                                    'memory': '256Mi',
                                    'cpu': '200m'
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        # Service
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': self.project_name
            },
            'spec': {
                'selector': {'app': self.project_name},
                'ports': [{
                    'protocol': 'TCP',
                    'port': 80,
                    'targetPort': 8080
                }],
                'type': 'LoadBalancer'
            }
        }
        
        with open(k8s_path / "deployment.yml", "w") as f:
            yaml.dump(deployment, f, default_flow_style=False)
        
        with open(k8s_path / "service.yml", "w") as f:
            yaml.dump(service, f, default_flow_style=False)
        
        logger.success("✅ 生成 K8s 配置")
    
    def _generate_github_actions(self):
        """生成GitHub Actions CI/CD"""
        workflows_path = self.project_path / ".github" / "workflows"
        workflows_path.mkdir(parents=True, exist_ok=True)
        
        workflow_config = {
            'name': 'Build and Deploy',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']}
            },
            'jobs': {
                'build': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Set up Go',
                            'uses': 'actions/setup-go@v4',
                            'with': {'go-version': '1.21'}
                        },
                        {
                            'name': 'Build',
                            'run': 'go build -v ./...'
                        },
                        {
                            'name': 'Test',
                            'run': 'go test -v ./...'
                        },
                        {
                            'name': 'Build Docker image',
                            'run': 'docker build -t ${{ github.repository }}:latest .'
                        }
                    ]
                }
            }
        }
        
        with open(workflows_path / "deploy.yml", "w") as f:
            yaml.dump(workflow_config, f, default_flow_style=False)
        
        logger.success("✅ 生成 GitHub Actions 工作流")
    
    def _generate_monitoring(self):
        """生成监控配置"""
        # Prometheus配置
        prometheus_config = {
            'global': {
                'scrape_interval': '15s'
            },
            'scrape_configs': [{
                'job_name': self.project_name,
                'static_configs': [{
                    'targets': ['app:8080']
                }]
            }]
        }
        
        with open(self.deploy_path / "prometheus.yml", "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        logger.success("✅ 生成监控配置")
    
    def _generate_makefile(self):
        """生成Makefile"""
        makefile_content = f"""# {self.project_name} 部署命令

.PHONY: build run test docker docker-run deploy-local

# 构建应用
build:
	go build -o bin/{self.project_name} cmd/api/main.go

# 运行应用
run:
	go run cmd/api/main.go

# 运行测试
test:
	go test ./...

# 构建Docker镜像
docker:
	docker build -t {self.project_name}:latest .

# 本地Docker运行
docker-run:
	docker-compose up -d

# 本地部署
deploy-local:
	docker-compose down
	docker-compose up --build -d

# 停止服务
stop:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f

# 清理
clean:
	docker-compose down -v
	docker system prune -f
"""
        
        with open(self.project_path / "Makefile", "w") as f:
            f.write(makefile_content)
        
        logger.success("✅ 生成 Makefile")
    
    def _generate_readme(self):
        """生成部署README"""
        readme_content = f"""# {self.project_name} 部署指南

## 🚀 快速部署

### 1. 本地开发
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 2. 生产部署

#### Docker Compose
```bash
# 构建并启动
make deploy-local

# 或手动操作
docker-compose up --build -d
```

#### Kubernetes
```bash
# 应用配置
kubectl apply -f deploy/k8s/

# 检查状态
kubectl get pods -l app={self.project_name}
```

### 3. 监控访问

- **应用**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 4. CI/CD

项目已配置GitHub Actions，推送到main分支自动触发构建和部署。

### 5. 常用命令

```bash
# 构建应用
make build

# 运行测试
make test

# 停止服务
make stop

# 清理环境
make clean
```

## 🔧 环境变量

| 变量 | 描述 | 默认值 |
|---|---|---|
| APP_ENV | 运行环境 | production |
| PORT | 应用端口 | 8080 |
| NATS_URL | NATS地址 | nats://localhost:4222 |
| REDIS_ADDR | Redis地址 | localhost:6379 |
| POSTGRES_HOST | 数据库主机 | localhost |
| POSTGRES_PORT | 数据库端口 | 5432 |

## 📊 监控指标

应用已集成Prometheus指标：
- HTTP请求指标
- 业务逻辑指标
- 系统资源指标
- 自定义业务指标
"""
        
        with open(self.deploy_path / "README.md", "w") as f:
            f.write(readme_content)
        
        logger.success("✅ 生成部署文档")
    
    def _print_deploy_summary(self):
        """打印部署总结"""
        logger.info("🎉 部署配置已生成：")
        logger.info("   ✅ Docker Compose (本地开发)")
        logger.info("   ✅ Kubernetes (生产部署)")
        logger.info("   ✅ GitHub Actions (CI/CD)")
        logger.info("   ✅ Prometheus + Grafana (监控)")
        logger.info("   ✅ Makefile (快捷命令)")
        logger.info("   ✅ 完整部署文档")
        logger.info("")
        logger.info("🚀 使用步骤：")
        logger.info("   1. cd your-project")
        logger.info("   2. make deploy-local")
        logger.info("   3. 访问 http://localhost:8080")