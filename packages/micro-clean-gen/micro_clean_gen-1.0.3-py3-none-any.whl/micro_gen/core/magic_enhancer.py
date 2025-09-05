"""
Magic Enhancer - 一键式完整微服务初始化
将 init, es, session, task, saga 和 projection 串行调用，一步到位
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger

from .simple_enhancer import SimpleEnhancer
from .base_generator import BaseGenerator
from .deploy_generator import DeployGenerator


class MagicEnhancer:
    """魔法增强器 - 一键完成所有功能集成"""
    
    def __init__(self, project_path: Path, project_name: str = "magic-service"):
        self.project_path = project_path
        self.project_name = project_name
        self.simple_enhancer = SimpleEnhancer(project_path)
        self.config_path = None
    
    def magic_init(self, config_path: Optional[str] = None, force: bool = False):
        """
        魔法初始化 - 一键完成所有功能
        
        执行顺序：
        1. 初始化项目结构
        2. 添加ES事件系统
        3. 添加会话管理
        4. 添加任务系统
        5. 添加Saga事务
        6. 添加投影机制
        
        Args:
            config_path: 可选的配置文件路径
            force: 是否强制覆盖现有文件
        """
        self.config_path = config_path
        logger.info("🪄 启动魔法初始化模式...")
        
        if config_path:
            logger.info(f"📋 使用配置文件: {config_path}")
        
        try:
            # 步骤1: 初始化项目
            logger.info("📁 步骤1/6: 初始化项目结构...")
            self._init_project_structure()
            
            # 步骤2: 添加ES事件系统
            logger.info("⚡ 步骤2/6: 集成ES事件系统...")
            self._add_es_system()
            
            # 步骤3: 添加会话管理
            logger.info("🔐 步骤3/6: 集成会话管理...")
            self._add_session_system()

            # 步骤4: 添加任务系统
            logger.info("📋 步骤4/6: 集成任务系统...")
            self._add_task_system()

            # 步骤5: 添加Saga事务
            logger.info("🔄 步骤5/6: 集成Saga事务...")
            self._add_saga_system()
            
            # 步骤6: 添加投影机制
            logger.info("🎯 步骤6/6: 集成投影机制...")
            self._add_projection_system()
            
            # 步骤7: 生成部署配置
            logger.info("🚀 生成完整部署配置...")
            deploy_gen = DeployGenerator(self.project_path, self.project_name)
            deploy_gen.generate_all()
            
            logger.success("✨ 魔法初始化完成！您的微服务已全副武装！")
            self._print_magic_summary()
            
        except Exception as e:
            logger.error(f"❌ 魔法初始化失败: {e}")
            raise
    
    def _execute_cli_command(self, command_parts: list, working_dir: str = None):
        """执行CLI命令的通用方法"""
        import subprocess
        import os
        from pathlib import Path
        
        env = os.environ.copy()
        # 使用绝对路径确保无论在哪个目录都能找到micro_gen
        micro_gen_path = str(Path(__file__).parent.parent.parent)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{micro_gen_path}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = micro_gen_path
        
        cwd = working_dir or str(self.project_path)
        
        cmd = ["python", "-m", "micro_gen.cli"] + command_parts
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
        
        if result.returncode != 0:
            logger.error(f"执行 {' '.join(command_parts)} 命令失败: {result.stderr}")
            return False
        else:
            logger.success(f"✅ {' '.join(command_parts)} 命令执行完成！")
            return True

    def _init_project_structure(self):
        """初始化项目结构"""
        logger.info("📁 初始化项目结构...")
        
        # 确保父目录存在
        self.project_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = self._execute_cli_command(["init", str(self.project_name)], working_dir=str(self.project_path.parent))
        if not success:
            raise RuntimeError("项目初始化失败")

    def _add_es_system(self):
        """添加ES事件系统"""
        logger.info("⚡ 添加事件溯源系统...")
        self._execute_cli_command(["es"])

    def _add_session_system(self):
        """添加会话管理"""
        logger.info("🔐 添加会话管理...")
        self._execute_cli_command(["session"])

    def _add_task_system(self):
        """添加任务系统"""
        logger.info("📋 添加任务系统...")
        self._execute_cli_command(["task"])

    def _add_saga_system(self):
        """添加Saga事务"""
        logger.info("🔄 添加Saga事务...")
        self._execute_cli_command(["saga"])

    def _add_projection_system(self):
        """添加投影系统"""
        logger.info("🎯 添加投影机制...")
        self._execute_cli_command(["projection"])
    
    def _print_magic_summary(self):
        """打印魔法初始化总结"""
        logger.success("✨ 魔法初始化完成！您的微服务已全副武装！")
        logger.info("📋 生成的功能：")
        logger.info("   ✅ 整洁架构 (Clean Architecture)")
        logger.info("   ✅ 事件溯源 (Event Sourcing)")
        logger.info("   ✅ 会话管理 (Session)")
        logger.info("   ✅ 任务调度 (Task)")
        logger.info("   ✅ Saga分布式事务")
        logger.info("   ✅ 投影机制 (Projection)")
        logger.info("   ✅ Docker部署 (Docker)")
        logger.info("   ✅ Kubernetes部署 (K8s)")
        logger.info("   ✅ CI/CD流水线")
        logger.info("   ✅ 监控告警 (Prometheus + Grafana)")
        logger.info("   ✅ 一键部署脚本")
        logger.info("")
        logger.info("🚀 下一步：")
        logger.info("   1. cd your-project")
        logger.info("   2. go mod tidy")
        logger.info("   3. docker-compose up -d (启动依赖服务)")
        logger.info("   4. go run cmd/api/main.go")