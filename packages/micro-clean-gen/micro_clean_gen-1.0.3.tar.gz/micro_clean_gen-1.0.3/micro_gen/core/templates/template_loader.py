"""
模板加载器 - 使用Jinja2模板引擎
提供统一的模板渲染功能
"""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class TemplateLoader:
    """增强的模板加载器"""
    
    def __init__(self, template_dir: Path):
        """初始化模板加载器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = Path(template_dir)
        if not self.template_dir.exists():
            raise FileNotFoundError(f"模板目录不存在: {self.template_dir}")
        
        # 使用Jinja2模板引擎
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # 添加自定义过滤器
        self.env.filters['camel_case'] = self._to_camel_case
        self.env.filters['snake_case'] = self._to_snake_case
        self.env.filters['lower_camel'] = self._to_lower_camel_case
    
    def load_template(self, template_path: str) -> str:
        """加载模板文件
        
        Args:
            template_path: 相对于模板目录的路径
            
        Returns:
            模板内容
        """
        try:
            template = self.env.get_template(template_path)
            return template.render()
        except TemplateNotFound:
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
    
    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """渲染模板
        
        Args:
            template_path: 模板路径
            context: 渲染上下文
            
        Returns:
            渲染后的内容
        """
        try:
            template = self.env.get_template(template_path)
            return template.render(**context)
        except TemplateNotFound as e:
            logger.error(f"模板文件未找到: {template_path}")
            raise
        except Exception as e:
            logger.error(f"模板渲染失败 {template_path}: {e}")
            raise
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """渲染字符串模板
        
        Args:
            template_string: 模板字符串
            context: 渲染上下文
            
        Returns:
            渲染后的内容
        """
        template = self.env.from_string(template_string)
        return template.render(**context)
    
    def list_templates(self) -> list:
        """列出所有可用的模板文件"""
        return self.env.list_templates()
    
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """将蛇形命名转换为驼峰命名"""
        if not snake_str:
            return snake_str
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def _to_snake_case(camel_str: str) -> str:
        """将驼峰命名转换为蛇形命名"""
        import re
        if not camel_str:
            return camel_str
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def _to_lower_camel_case(snake_str: str) -> str:
        """将蛇形命名转换为小驼峰命名"""
        if not snake_str:
            return snake_str
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])


class TemplateManager:
    """模板管理器 - 统一管理多个模板目录"""
    
    def __init__(self, base_template_dir: Path):
        """初始化模板管理器
        
        Args:
            base_template_dir: 基础模板目录
        """
        self.base_template_dir = Path(base_template_dir)
        self.loaders = {}
    
    def get_loader(self, template_type: str) -> TemplateLoader:
        """获取特定类型的模板加载器
        
        Args:
            template_type: 模板类型（如 'init', 'es', 'session' 等）
            
        Returns:
            模板加载器实例
        """
        if template_type not in self.loaders:
            template_dir = self.base_template_dir / template_type
            if template_dir.exists():
                self.loaders[template_type] = TemplateLoader(template_dir)
            else:
                raise FileNotFoundError(f"模板类型不存在: {template_type}")
        
        return self.loaders[template_type]
    
    def render_template(self, template_type: str, template_name: str, context: Dict[str, Any]) -> str:
        """便捷方法，直接渲染特定类型的模板
        
        Args:
            template_type: 模板类型
            template_name: 模板名称
            context: 渲染上下文
            
        Returns:
            渲染后的内容
        """
        loader = self.get_loader(template_type)
        return loader.render_template(template_name, context)
    
    def get_available_types(self) -> list:
        """获取所有可用的模板类型"""
        if not self.base_template_dir.exists():
            return []
        
        return [d.name for d in self.base_template_dir.iterdir() 
                if d.is_dir() and not d.name.startswith('.')]