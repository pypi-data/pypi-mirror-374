"""
微服务代码生成器 - 基于整洁架构的事件驱动微服务代码生成器
"""

__version__ = "1.0.0"
__author__ = "Ray"
__email__ = "ray@rayinfo.cn"
__description__ = "基于整洁架构的事件驱动微服务代码生成器"

from .cli import main

__all__ = [
    "main",
    "__version__",
]