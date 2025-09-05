#!/usr/bin/env python3
"""
微服务代码生成器命令行接口 - 重构版
"""

import os
import sys
import shutil
from pathlib import Path

import click
from loguru import logger

from micro_gen.core.templates.template_loader import TemplateLoader


def main():
    cli()


@click.group()
def cli():
    """微服务代码生成器命令行工具"""
    pass


@cli.command()
@click.argument("project_name")
def init(project_name: str):
    """初始化新的微服务项目 - 基于整洁架构和Go官方实践"""
    # 检查当前目录下是否有同名目录，没有就创建
    project_path = Path.cwd() / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    # 使用项目初始化器
    initializer = ProjectInitializer(project_name, project_path)
    initializer.init_project()

    logger.success(f"✅ 项目 '{project_name}' 初始化完成！")
    logger.info(f"📁 项目路径: {project_path}")
    logger.info("🚀 下一步:")
    logger.info(f"  cd {project_name}")
    logger.info("  make deps    # 安装依赖")
    logger.info("  make run     # 运行服务")


@cli.command()
@click.option("--force", is_flag=True, help="强制覆盖现有文件")
def es(force: bool):
    """为现有项目添加ES事件机制 - 基于NATS JetStream"""
    enhancer = ProjectEnhancer(Path.cwd())
    enhancer.add_es_event_system()


@cli.command()
@click.option('--path', default='.', help='项目路径')
def session(path):
    """为现有项目添加会话管理能力 - 极简设计，一行代码即可使用"""
    from micro_gen.core.simple_enhancer import SimpleEnhancer
    enhancer = SimpleEnhancer(Path(path))
    enhancer.add_simple_session()


@cli.command()
@click.option('--path', default='.', help='项目路径')
def saga(path):
    """为现有项目添加Saga事务 - 极简设计，一行代码即可使用"""
    from micro_gen.core.simple_enhancer import SimpleEnhancer
    enhancer = SimpleEnhancer(Path(path))
    enhancer.add_simple_saga()


@cli.command()
@click.option('--path', default='.', help='项目路径')
@click.option('--config', default=None, help='CRUD配置文件路径')
@click.option('--entity', default=None, help='实体名称（简单模式）')
@click.option('--fields', default=None, help='字段定义，格式：name:type,name:type...')
def crud(path, config, entity, fields):
    """🔧 一键CRUD - 自动生成实体、仓库、Handler、路由和测试
    
    根据实体配置一键生成完整的CURD操作：
    • 实体定义 (entity)
    • 数据仓库 (repository)
    • REST API Handler
    • 路由注册
    • 单元测试
    
    使用方式：
    
    1. 配置文件模式：
       micro-gen crud --config ./examples/crud-config.yaml
    
    2. 简单模式：
       micro-gen crud --entity user --fields "username:string,email:string,age:int"
    
    3. 指定项目路径：
       micro-gen crud --path ./my-project --entity product --fields "name:string,price:float"
    """
    from micro_gen.core.crud_generator import CRUDGenerator
    
    project_path = Path(path)
    project_name = "your-project"  # 可以从go.mod读取
    
    generator = CRUDGenerator(project_path, project_name)
    
    if config:
        # 配置文件模式
        generator.generate_from_config(Path(config))
    elif entity and fields:
        # 简单模式
        field_dict = {}
        for field in fields.split(','):
            if ':' in field:
                name, type_str = field.split(':', 1)
                field_dict[name.strip()] = type_str.strip()
        generator.generate_from_simple(entity, field_dict)
    else:
        logger.error("请提供配置文件或使用简单模式 (--entity + --fields)")
        return


@cli.command()
@click.option('--path', default='.', help='项目路径')
@click.option('--name', default='micro-service', help='服务名称')
@click.option('--env', default='dev', help='部署环境 (dev/prod)')
def deploy(path, name, env):
    """🚀 一键部署 - 生成完整部署配置
    
    自动生成：
    • Docker 镜像构建配置
    • Kubernetes 部署清单
    • docker-compose 本地开发环境
    • CI/CD GitHub Actions 工作流
    
    示例:
        micro-gen deploy --name my-service
        micro-gen deploy --path ./my-project --name awesome-service --env prod
    """
    from micro_gen.core.deploy_generator import DeployGenerator
    
    project_path = Path(path)
    deployer = DeployGenerator(project_path, name)
    deployer.generate_all()


@cli.command()
@click.option('--path', default='.', help='项目路径')
@click.option('--name', default='magic-service', help='项目名称')
@click.option('--config', default=None, help='配置文件路径 (可选)')
@click.option('--force', is_flag=True, help='强制覆盖现有文件')
def magic(path, name, config, force):
    """🪄 魔法初始化 - 一键完成所有功能集成！
    
    自动执行：init → es → session → task → saga → projection
    创建完整的微服务，包含事件溯源、会话、任务、事务和投影机制
    
    示例:
        micro-gen magic --name my-service
        micro-gen magic --path ./my-project --name awesome-service
        micro-gen magic --config ./my-config.yaml --name full-stack-service
    """
    from micro_gen.core.magic_enhancer import MagicEnhancer
    
    project_path = Path(path)
    enhancer = MagicEnhancer(project_path, name)
    enhancer.magic_init(config_path=config, force=force)


class ProjectInitializer:
    """项目初始化器"""
    
    def __init__(self, project_name: str, project_path: Path):
        self.project_name = project_name
        self.project_path = project_path
        self.template_loader = TemplateLoader(Path(__file__).parent / "core" / "templates" / "init")
    
    def init_project(self):
        """初始化项目结构"""
        self._create_directories()
        self._generate_files()
    
    def _create_directories(self):
        """创建项目目录结构"""
        directories = [
            "cmd/api",
            "data", "data/snapshots",
            "internal/entity", "internal/usecase", "adapter/handler", "adapter/repo",
            "pkg/config", "pkg/logger", "pkg/db", "pkg/http"
        ]
        
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_files(self):
        """生成项目文件"""
        templates = {
            "go.mod": "go_mod.tmpl",
            "cmd/api/main.go": "main.go.tmpl",
            "pkg/config/config.go": "config.go.tmpl",
            "pkg/logger/logger.go": "logger.go.tmpl",
            "adapter/handler/health_handler.go": "health_handler.go.tmpl",
            "pkg/http/router.go": "router.go.tmpl",
            "Makefile": "makefile.tmpl",
            "Dockerfile": "dockerfile.tmpl",
            ".env": "env.tmpl",
            ".gitignore": "gitignore.tmpl"
        }
        
        context = {"project_name": self.project_name}
        for file_path, template_name in templates.items():
            content = self.template_loader.render_template(template_name, context)
            (self.project_path / file_path).write_text(content)


class ProjectEnhancer:
    """项目增强器 - 为现有项目添加功能模块"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_name = self._get_project_name()
    
    def _get_project_name(self):
        """从go.mod获取项目名"""
        go_mod_file = self.project_path / "go.mod"
        if not go_mod_file.exists():
            logger.error("项目必须已初始化（需要go.mod文件）")
            sys.exit(1)
        
        content = go_mod_file.read_text()
        for line in content.split("\n"):
            if line.startswith("module "):
                return line.replace("module ", "").strip()
        
        logger.error("无法从go.mod中读取项目名")
        sys.exit(1)
    
    def add_es_event_system(self):
        """添加ES事件机制"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加ES事件机制...")
        
        enhancer = ModuleEnhancer(self.project_path, self.project_name, "es")
        enhancer.add_module([
            "internal/entity",
            "internal/usecase/event",
            "pkg/event"
        ], [
            ("internal/entity/event.go", "entity_event.go.tmpl"),
            ("internal/usecase/event/bus.go", "event_bus.go.tmpl"),
            ("internal/usecase/event/snapshot.go", "event_snapshot.go.tmpl"),
            ("internal/usecase/event/store.go", "event_store.go.tmpl"),
            ("pkg/event/jetstream_store.go", "jetstream_store.go.tmpl"),
            ("pkg/event/jetstream_bus.go", "jetstream_bus.go.tmpl"),
            ("pkg/event/snapshot_store.go", "snapshot_store.go.tmpl"),
            ("pkg/event/example_usage.go", "example_usage.go.tmpl")
        ])
        
        enhancer.update_config({
            "NATSURL": "getEnv(\"NATS_URL\", \"nats://localhost:4222\")",
            "StreamName": "getEnv(\"NATS_STREAM_NAME\", \"events\")",
            "ClusterName": "getEnv(\"NATS_CLUSTER_NAME\", \"micro-services\")"
        })
        
        logger.success("✅ ES事件机制添加完成！")
        self._print_next_steps([
            "go get github.com/nats-io/nats.go",
            "docker run -d -p 4222:4222 nats:latest"
        ])
    
    def add_session_management(self):
        """添加会话管理"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加会话管理能力...")
        
        enhancer = ModuleEnhancer(self.project_path, self.project_name, "session")
        enhancer.add_module([
            "internal/entity",
            "internal/usecase/session",
            "pkg/session"
        ], [
            ("internal/entity/session.go", "entity_session.go.tmpl"),
            ("internal/usecase/session/service.go", "usecase_session.go.tmpl"),
            ("pkg/session/redis_store.go", "redis_store.go.tmpl"),
            ("pkg/session/memory_store.go", "memory_store.go.tmpl"),
            ("pkg/session/badger_store.go", "badger_store.go.tmpl"),
            ("pkg/session/session_manager.go", "session_manager.go.tmpl")
        ])
        
        enhancer.update_config({
            "SessionLevel": "getEnv(\"SESSION_LEVEL\", \"low\")",
            "RedisAddr": "getEnv(\"REDIS_ADDR\", \"localhost:6379\")",
            "RedisPassword": "getEnv(\"REDIS_PASSWORD\", \"\")",
            "RedisDB": "getEnvAsInt(\"REDIS_DB\", 0)"
        })
        
        logger.success("✅ 会话管理能力添加完成！")
        self._print_next_steps([
            "go get github.com/redis/go-redis/v9",
            "go get github.com/dgraph-io/badger/v4"
        ])
    
    def add_saga_management(self):
        """添加Saga管理"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加Saga分布式事务管理能力...")
        
        enhancer = ModuleEnhancer(self.project_path, self.project_name, "saga")
        enhancer.add_module([
            "internal/entity",
            "internal/usecase/saga",
            "pkg/saga"
        ], [
            ("internal/entity/saga.go", "entity_saga.go.tmpl"),
            ("internal/usecase/saga/service.go", "usecase_saga.go.tmpl"),
            ("pkg/saga/saga_store.go", "saga_store.go.tmpl"),
            ("pkg/saga/saga_manager.go", "saga_manager.go.tmpl"),
            ("pkg/saga/example_usage.go", "example_usage.go.tmpl")
        ])
        
        logger.success("✅ Saga分布式事务管理能力添加完成！")

    def add_projection_mechanism(self):
        """添加投影机制"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加投影机制...")
        
        enhancer = ModuleEnhancer(self.project_path, self.project_name, "projection")
        enhancer.add_module([
            "internal/entity",
            "internal/usecase/projection",
            "pkg/projection"
        ], [
            ("internal/entity/projection.go", "entity_projection.go.tmpl"),
            ("internal/usecase/projection/service.go", "example_usage.go.tmpl"),
            ("pkg/projection/projection_store.go", "projection_store.go.tmpl")
        ])
        
        logger.success("✅ 投影机制添加完成！")
        self._print_next_steps([
            "go get github.com/redis/go-redis/v9",
            "go get github.com/dgraph-io/badger/v4"
        ])
    
    def _print_next_steps(self, steps):
        """打印后续步骤"""
        logger.info("🚀 下一步:")
        for step in steps:
            logger.info(f"  {step}")


class ModuleEnhancer:
    """模块增强器 - 处理具体模块的添加"""
    
    def __init__(self, project_path: Path, project_name: str, module_type: str):
        self.project_path = project_path
        self.project_name = project_name
        self.module_type = module_type
        self.template_loader = TemplateLoader(
            Path(__file__).parent / "core" / "templates" / module_type
        )
    
    def add_module(self, directories: list, files: list):
        """添加模块"""
        # 创建目录
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
        
        # 生成文件
        context = {"project_name": self.project_name}
        for file_path, template_name in files:
            content = self.template_loader.render_template(template_name, context)
            (self.project_path / file_path).write_text(content)
    
    def update_config(self, config_fields: dict):
        """更新配置文件"""
        config_file = self.project_path / "pkg" / "config" / "config.go"
        if not config_file.exists():
            logger.warning("⚠️  配置文件不存在，跳过配置更新")
            return
        
        content = config_file.read_text()
        
        # 添加结构体字段
        struct_end = "\tLogLevel string\n}"
        if struct_end in content:
            new_fields = "\tLogLevel string\n\n\t// " + self.module_type.upper() + "配置\n"
            for field, default in config_fields.items():
                new_fields += f"\t{field} string\n"
            content = content.replace(struct_end, new_fields + "}")
        
        # 添加Load函数默认值
        load_end = "\t\tLogLevel:   getEnv(\"LOG_LEVEL\", \"info\"),\n\t}\n\n\treturn config, nil\n}"
        if load_end in content:
            new_load = "\t\tLogLevel:   getEnv(\"LOG_LEVEL\", \"info\"),\n"
            for field, default in config_fields.items():
                new_load += f"\t\t{field}: {default},\n"
            new_load += "\t}\n\n\treturn config, nil\n}"
            content = content.replace(load_end, new_load)
        
        config_file.write_text(content)
        logger.success(f"✅ {self.module_type}配置已添加到 pkg/config/config.go")


@cli.command()
def projection():
    """为现有项目添加投影机制 - 支持事件溯源读模型"""
    enhancer = ProjectEnhancer(Path.cwd())
    enhancer.add_projection_mechanism()


@cli.command()
@click.option("--force", is_flag=True, help="强制覆盖现有文件")
def es(force: bool):
    """为现有项目添加ES事件机制 - 基于NATS JetStream"""
    enhancer = ProjectEnhancer(Path.cwd())
    enhancer.add_es_event_system()


@cli.command()
@click.option('--path', default='.', help='项目路径')
def session(path):
    """为现有项目添加会话管理能力 - 极简设计，一行代码即可使用"""
    from micro_gen.core.simple_enhancer import SimpleEnhancer
    enhancer = SimpleEnhancer(Path(path))
    enhancer.add_simple_session()


@cli.command()
@click.option('--path', default='.', help='项目路径')
def task(path):
    """为现有项目添加任务系统 - 极简设计，一行代码即可使用"""
    from micro_gen.core.simple_enhancer import SimpleEnhancer
    enhancer = SimpleEnhancer(Path(path))
    enhancer.add_simple_task()


@cli.command()
@click.option('--path', default='.', help='项目路径')
def saga(path):
    """为现有项目添加Saga事务 - 极简设计，一行代码即可使用"""
    from micro_gen.core.simple_enhancer import SimpleEnhancer
    enhancer = SimpleEnhancer(Path(path))
    enhancer.add_simple_saga()


class ModuleEnhancer:
    """模块增强器 - 处理具体模块的添加"""
    
    def __init__(self, project_path: Path, project_name: str, module_type: str):
        self.project_path = project_path
        self.project_name = project_name
        self.module_type = module_type
        self.template_loader = TemplateLoader(
            Path(__file__).parent / "core" / "templates" / module_type
        )
    
    def add_module(self, directories: list, files: list):
        """添加模块"""
        # 创建目录
        for directory in directories:
            (self.project_path / directory).mkdir(parents=True, exist_ok=True)
        
        # 生成文件
        context = {"project_name": self.project_name}
        for file_path, template_name in files:
            content = self.template_loader.render_template(template_name, context)
            (self.project_path / file_path).write_text(content)
    
    def update_config(self, config_fields: dict):
        """更新配置文件"""
        config_file = self.project_path / "pkg" / "config" / "config.go"
        if not config_file.exists():
            logger.warning("⚠️  配置文件不存在，跳过配置更新")
            return
        
        content = config_file.read_text()
        
        # 添加结构体字段
        struct_end = "\tLogLevel string\n}"
        if struct_end in content:
            new_fields = "\tLogLevel string\n\n\t// " + self.module_type.upper() + "配置\n"
            for field, default in config_fields.items():
                new_fields += f"\t{field} string\n"
            content = content.replace(struct_end, new_fields + "}")
        
        # 添加Load函数默认值
        load_end = "\t\tLogLevel:   getEnv(\"LOG_LEVEL\", \"info\"),\n\t}\n\n\treturn config, nil\n}"
        if load_end in content:
            new_load = "\t\tLogLevel:   getEnv(\"LOG_LEVEL\", \"info\"),\n"
            for field, default in config_fields.items():
                new_load += f"\t\t{field}: {default},\n"
            new_load += "\t}\n\n\treturn config, nil\n}"
            content = content.replace(load_end, new_load)
        
        config_file.write_text(content)
        logger.success(f"✅ {self.module_type}配置已添加到 pkg/config/config.go")


@cli.command()
def projection():
    """为现有项目添加投影机制 - 支持事件溯源读模型"""
    enhancer = ProjectEnhancer(Path.cwd())
    enhancer.add_projection_mechanism()







if __name__ == "__main__":
    main()
