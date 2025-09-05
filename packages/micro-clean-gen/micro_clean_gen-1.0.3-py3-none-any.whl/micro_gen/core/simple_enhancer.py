#!/usr/bin/env python3
"""
简化版增强器 - 与现有系统完美配合
"""

from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from micro_gen.core.templates.template_loader import TemplateLoader
from micro_gen.core.utils import logger

class SimpleEnhancer:
    """极简增强器 - 为现有项目添加功能"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_name = self._get_project_name()
        self.template_loader = TemplateLoader(Path(__file__).parent / "templates" / "simple")
    
    def _get_project_name(self):
        """从go.mod获取项目名"""
        go_mod_file = self.project_path / "go.mod"
        if not go_mod_file.exists():
            logger.error("项目必须已初始化（需要go.mod文件）")
            return "your-project"
        
        content = go_mod_file.read_text()
        for line in content.split("\n"):
            if line.startswith("module "):
                return line.replace("module ", "").strip()
        
        return "your-project"
    
    def add_simple_session(self):
        """添加简化版会话管理"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加简化版会话管理...")
        
        # 创建目录
        session_dir = self.project_path / "pkg" / "session"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成核心文件
        context = {"project_name": self.project_name}
        content = self.template_loader.render_template("session.go.tmpl", context)
        (session_dir / "session.go").write_text(content)
        
        logger.info("✅ 简化版会话管理添加完成！（仅需1个文件，50行代码）")
        logger.info("使用示例: session.NewManager(session.NewMemoryStore(), time.Hour)")
    
    def add_simple_task(self):
        """添加简化版任务系统"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加简化版任务系统...")
        
        # 创建目录
        task_dir = self.project_path / "pkg" / "task"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成核心文件
        context = {"project_name": self.project_name}
        content = self.template_loader.render_template("task.go.tmpl", context)
        (task_dir / "task.go").write_text(content)
        
        logger.info("✅ 简化版任务系统添加完成！（仅需1个文件，80行代码）")
        logger.info("使用示例: worker := task.NewWorker(task.NewMemoryStore())")
    
    def add_simple_saga(self):
        """添加简化版Saga事务"""
        logger.info(f"🚀 为项目 '{self.project_name}' 添加简化版Saga事务...")
        
        # 创建目录
        saga_dir = self.project_path / "pkg" / "saga"
        saga_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成核心文件
        context = {"project_name": self.project_name}
        content = self.template_loader.render_template("saga.go.tmpl", context)
        (saga_dir / "saga.go").write_text(content)
        
        logger.info("✅ 简化版Saga事务添加完成！（仅需1个文件，100行代码）")
        logger.info("使用示例: coordinator := saga.NewCoordinator(saga.NewMemoryStore())")

# 命令行接口
if __name__ == "__main__":
    import click
    
    @click.command()
    @click.option('--path', default='.', help='项目路径')
    def simple_session(path):
        """添加简化版会话管理"""
        enhancer = SimpleEnhancer(Path(path))
        enhancer.add_simple_session()
    
    @click.command()
    @click.option('--path', default='.', help='项目路径')
    def simple_task(path):
        """添加简化版任务系统"""
        enhancer = SimpleEnhancer(Path(path))
        enhancer.add_simple_task()
    
    @click.command()
    @click.option('--path', default='.', help='项目路径')
    def simple_saga(path):
        """添加简化版Saga事务"""
        enhancer = SimpleEnhancer(Path(path))
        enhancer.add_simple_saga()
    
    # 注册命令
    simple_session()
    simple_task()
    simple_saga()