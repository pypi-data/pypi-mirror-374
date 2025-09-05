"""
基础生成器 - 所有生成器的基类
提供统一的代码生成接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .utils import (
    ConfigManager, PathBuilder, CodeGenerator, ValidationUtils,
    NamingConverter
)
from .templates.template_loader import TemplateManager

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """基础生成器类"""
    
    def __init__(self, project_path: Path, config: Dict[str, Any] = None):
        """初始化生成器
        
        Args:
            project_path: 项目根目录
            config: 项目配置
        """
        self.project_path = Path(project_path)
        self.config = config or {}
        self.template_manager = TemplateManager(
            Path(__file__).parent / "templates"
        )
        
        # 确保项目目录存在
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # 加载项目配置
        self._load_project_config()
    
    def _load_project_config(self) -> None:
        """加载项目配置文件"""
        config_path = self.project_path / "micro-gen.yaml"
        if config_path.exists():
            self.config = ConfigManager.load_config(config_path)
    
    def _save_project_config(self) -> None:
        """保存项目配置文件"""
        config_path = self.project_path / "micro-gen.yaml"
        ConfigManager.save_config(config_path, self.config)
    
    def _update_project_config(self, updates: Dict[str, Any]) -> None:
        """更新项目配置"""
        config_path = self.project_path / "micro-gen.yaml"
        self.config = ConfigManager.update_config(config_path, updates)
    
    def validate_config(self) -> List[str]:
        """验证配置有效性
        
        Returns:
            错误信息列表
        """
        errors = []
        
        # 验证项目名
        project_name = self.config.get('project_name', '')
        if not ValidationUtils.validate_package_name(project_name):
            errors.append(f"无效的项目名: {project_name}")
        
        # 验证模块名
        module_name = self.config.get('module_name', '')
        if module_name and not ValidationUtils.validate_package_name(module_name):
            errors.append(f"无效的模块名: {module_name}")
        
        return errors
    
    def generate_file(self, file_path: Path, content: str, 
                     overwrite: bool = False) -> None:
        """生成文件
        
        Args:
            file_path: 文件路径（相对于项目根目录）
            content: 文件内容
            overwrite: 是否覆盖已存在的文件
        """
        full_path = self.project_path / file_path
        CodeGenerator.generate_file(full_path, content, overwrite)
    
    def render_template(self, template_type: str, template_name: str, 
                       context: Dict[str, Any] = None) -> str:
        """渲染模板
        
        Args:
            template_type: 模板类型
            template_name: 模板名称
            context: 渲染上下文
            
        Returns:
            渲染后的内容
        """
        context = context or {}
        
        # 添加常用变量到上下文
        context.update({
            'project_name': self.config.get('project_name', 'microservice'),
            'module_name': self.config.get('module_name', 'github.com/example/microservice'),
            'package_name': NamingConverter.to_snake_case(
                self.config.get('project_name', 'microservice')
            ),
            'camel_case_name': NamingConverter.to_camel_case(
                self.config.get('project_name', 'microservice')
            ),
            **self.config
        })
        
        return self.template_manager.render_template(
            template_type, template_name, context
        )
    
    def create_directories(self, directories: List[Path]) -> None:
        """创建目录
        
        Args:
            directories: 目录路径列表（相对于项目根目录）
        """
        full_paths = [self.project_path / d for d in directories]
        PathBuilder.ensure_directories(full_paths)
    
    def get_context(self, **kwargs) -> Dict[str, Any]:
        """获取基础渲染上下文
        
        Returns:
            渲染上下文
        """
        return {
            'project_name': self.config.get('project_name', 'microservice'),
            'module_name': self.config.get('module_name', 'github.com/example/microservice'),
            'package_name': NamingConverter.to_snake_case(
                self.config.get('project_name', 'microservice')
            ),
            'camel_case_name': NamingConverter.to_camel_case(
                self.config.get('project_name', 'microservice')
            ),
            **self.config,
            **kwargs
        }
    
    @abstractmethod
    def generate(self) -> None:
        """生成代码的抽象方法
        
        子类必须实现此方法以提供具体的代码生成逻辑
        """
        pass
    
    def pre_generate(self) -> None:
        """生成前的准备工作
        
        子类可以重写此方法进行预处理
        """
        errors = self.validate_config()
        if errors:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
    
    def post_generate(self) -> None:
        """生成后的清理工作
        
        子类可以重写此方法进行后处理
        """
        pass
    
    def run(self) -> None:
        """运行生成器
        
        执行完整的生成流程
        """
        try:
            logger.info(f"开始生成代码: {self.__class__.__name__}")
            
            self.pre_generate()
            self.generate()
            self.post_generate()
            
            logger.info(f"代码生成完成: {self.__class__.__name__}")
        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            raise