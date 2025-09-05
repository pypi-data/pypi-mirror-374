"""
工具函数模块 - 按功能分离的工具集合
"""

import re
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class NamingConverter:
    """命名转换工具类"""
    
    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """蛇形命名转驼峰命名"""
        if not snake_str:
            return snake_str
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """驼峰命名转蛇形命名"""
        if not camel_str:
            return camel_str
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def to_lower_camel_case(snake_str: str) -> str:
        """蛇形命名转小驼峰命名"""
        if not snake_str:
            return snake_str
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])


class TypeMapper:
    """类型映射工具类"""
    
    _GO_TO_PROTO_MAP = {
        'string': 'string',
        'int': 'int32',
        'int32': 'int32',
        'int64': 'int64',
        'float32': 'float',
        'float64': 'double',
        'bool': 'bool',
        'time.Time': 'google.protobuf.Timestamp',
        '[]byte': 'bytes',
        '[]string': 'repeated string',
        '[]int': 'repeated int32',
        '[]int64': 'repeated int64',
        '[]float32': 'repeated float',
        '[]float64': 'repeated double',
        '[]bool': 'repeated bool',
    }
    
    _GO_TO_SQL_MAP = {
        'string': 'TEXT',
        'int': 'INTEGER',
        'int32': 'INTEGER',
        'int64': 'BIGINT',
        'float32': 'REAL',
        'float64': 'REAL',
        'bool': 'BOOLEAN',
        'time.Time': 'TIMESTAMP',
        '[]byte': 'BLOB',
    }
    
    @classmethod
    def go_to_proto(cls, go_type: str) -> str:
        """Go类型转Proto类型"""
        return cls._GO_TO_PROTO_MAP.get(go_type, 'string')
    
    @classmethod
    def go_to_sql(cls, go_type: str) -> str:
        """Go类型转SQL类型"""
        return cls._GO_TO_SQL_MAP.get(go_type, 'TEXT')


class ConfigManager:
    """配置管理工具类"""
    
    @staticmethod
    def load_config(config_path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"配置文件加载失败 {config_path}: {e}")
            return {}
    
    @staticmethod
    def save_config(config_path: Path, config: Dict[str, Any]) -> None:
        """保存配置文件"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"配置文件保存失败 {config_path}: {e}")
            raise
    
    @staticmethod
    def update_config(config_path: Path, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置文件"""
        config = ConfigManager.load_config(config_path)
        
        def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
            """深度更新字典"""
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(config, updates)
        ConfigManager.save_config(config_path, config)
        return config


class PathBuilder:
    """路径构建工具类"""
    
    @staticmethod
    def create_directory_structure(base_path: Path, structure: Dict[str, Any]) -> None:
        """创建目录结构"""
        def create_recursive(current_path: Path, struct: Dict[str, Any]) -> None:
            for name, content in struct.items():
                item_path = current_path / name
                
                if isinstance(content, dict):
                    # 创建目录
                    item_path.mkdir(parents=True, exist_ok=True)
                    create_recursive(item_path, content)
                elif isinstance(content, str):
                    # 创建文件
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                elif content is None:
                    # 仅创建目录
                    item_path.mkdir(parents=True, exist_ok=True)
        
        base_path.mkdir(parents=True, exist_ok=True)
        create_recursive(base_path, structure)
    
    @staticmethod
    def ensure_directories(directories: List[Path]) -> None:
        """确保目录存在"""
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


class CodeGenerator:
    """代码生成工具类"""
    
    @staticmethod
    def generate_file(file_path: Path, content: str, overwrite: bool = False) -> None:
        """生成文件"""
        if file_path.exists() and not overwrite:
            logger.warning(f"文件已存在，跳过: {file_path}")
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"文件已生成: {file_path}")
        except Exception as e:
            logger.error(f"文件生成失败 {file_path}: {e}")
            raise
    
    @staticmethod
    def append_to_file(file_path: Path, content: str) -> None:
        """追加内容到文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"内容已追加到: {file_path}")
        except Exception as e:
            logger.error(f"文件追加失败 {file_path}: {e}")
            raise


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_name(name: str, name_type: str = "entity") -> bool:
        """验证名称合法性"""
        if not name:
            return False
        
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        if not re.match(pattern, name):
            return False
        
        # 检查保留关键字
        go_keywords = {
            'break', 'default', 'func', 'interface', 'select',
            'case', 'defer', 'go', 'map', 'struct',
            'chan', 'else', 'goto', 'package', 'switch',
            'const', 'fallthrough', 'if', 'range', 'type',
            'continue', 'for', 'import', 'return', 'var'
        }
        
        return name.lower() not in go_keywords
    
    @staticmethod
    def validate_package_name(name: str) -> bool:
        """验证包名合法性"""
        return ValidationUtils.validate_name(name, "package")


# 向后兼容的函数
# 这些函数将在后续版本中移除，建议使用类方法

def to_camel_case(snake_str: str) -> str:
    """蛇形命名转驼峰命名（已废弃，使用NamingConverter.to_camel_case）"""
    return NamingConverter.to_camel_case(snake_str)


def to_snake_case(camel_str: str) -> str:
    """驼峰命名转蛇形命名（已废弃，使用NamingConverter.to_snake_case）"""
    return NamingConverter.to_snake_case(camel_str)


def to_lower_camel_case(snake_str: str) -> str:
    """蛇形命名转小驼峰命名（已废弃，使用NamingConverter.to_lower_camel_case）"""
    return NamingConverter.to_lower_camel_case(snake_str)


def load_config(config_path: Path) -> Dict[str, Any]:
    """加载配置文件（已废弃，使用ConfigManager.load_config）"""
    return ConfigManager.load_config(config_path)


def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """保存配置文件（已废弃，使用ConfigManager.save_config）"""
    ConfigManager.save_config(config_path, config)


def update_config(config_path: Path, updates: Dict[str, Any]) -> Dict[str, Any]:
    """更新配置文件（已废弃，使用ConfigManager.update_config）"""
    return ConfigManager.update_config(config_path, updates)


def create_directory_structure(base_path: Path, structure: Dict[str, Any]) -> None:
    """创建目录结构（已废弃，使用PathBuilder.create_directory_structure）"""
    PathBuilder.create_directory_structure(base_path, structure)


def validate_name(name: str, name_type: str = "entity") -> bool:
    """验证名称合法性（已废弃，使用ValidationUtils.validate_name）"""
    return ValidationUtils.validate_name(name, name_type)


def validate_package_name(name: str) -> bool:
    """验证包名合法性（已废弃，使用ValidationUtils.validate_package_name）"""
    return ValidationUtils.validate_package_name(name)


def get_go_type(field_type: str) -> str:
    """根据字段类型返回Go类型"""
    type_mapping = {
        'string': 'string',
        'int': 'int',
        'int64': 'int64',
        'float': 'float64',
        'float64': 'float64',
        'bool': 'bool',
        'datetime': 'time.Time',
        'time': 'time.Time',
        'uuid': 'string',
        'json': 'map[string]interface{}',
        'array': '[]interface{}',
        'text': 'string'
    }
    return type_mapping.get(field_type.lower(), 'string')


def get_json_tag(field_name: str) -> str:
    """生成JSON标签"""
    return f'`json:"{to_snake_case(field_name)}"`'


def get_validate_tag(field_type: str, required: bool = False) -> str:
    """生成验证标签"""
    if required:
        return f'`validate:"required"`'
    return ''


def get_field_assignment(field_name: str, prefix: str = '') -> str:
    """生成字段赋值语句"""
    if prefix:
        return f"{field_name}: {prefix}.{field_name},"
    return f"{field_name}: {field_name},"


def get_proto_type(field_type: str) -> str:
    """根据字段类型返回proto类型"""
    type_mapping = {
        'string': 'string',
        'int': 'int32',
        'int64': 'int64',
        'float': 'float',
        'float64': 'double',
        'bool': 'bool',
        'datetime': 'google.protobuf.Timestamp',
        'time': 'google.protobuf.Timestamp',
        'uuid': 'string',
        'json': 'string',
        'array': 'repeated string',
        'text': 'string'
    }
    return type_mapping.get(field_type.lower(), 'string')


def get_sql_type(field_type: str) -> str:
    """根据字段类型返回SQL类型"""
    type_mapping = {
        'string': 'VARCHAR(255)',
        'int': 'INTEGER',
        'int64': 'BIGINT',
        'float': 'FLOAT',
        'float64': 'DOUBLE',
        'bool': 'BOOLEAN',
        'datetime': 'TIMESTAMP',
        'time': 'TIME',
        'uuid': 'UUID',
        'json': 'JSON',
        'text': 'TEXT'
    }
    return type_mapping.get(field_type.lower(), 'VARCHAR(255)')


def generate_imports(imports: List[str]) -> str:
    """生成import语句"""
    if not imports:
        return ''
    
    import_lines = []
    standard_libs = []
    third_party_libs = []
    project_libs = []
    
    for imp in imports:
        if imp.startswith('"') and imp.endswith('"'):
            if imp.startswith('""') or imp.startswith('"go.'):
                standard_libs.append(imp)
            elif imp.startswith('"github.com') and not imp.startswith(f'"{get_project_name()}'):
                third_party_libs.append(imp)
            else:
                project_libs.append(imp)
    
    if standard_libs:
        import_lines.extend(sorted(standard_libs))
    
    if third_party_libs:
        import_lines.extend(sorted(third_party_libs))
    
    if project_libs:
        import_lines.extend(sorted(project_libs))
    
    if len(import_lines) == 1:
        return f'import {import_lines[0]}'
    
    return 'import (\n    ' + '\n    '.join(import_lines) + '\n)'


def get_project_name() -> str:
    """获取项目名称"""
    # 从环境变量或配置文件获取
    return os.getenv('PROJECT_NAME', 'microservice')


def validate_config(config: Dict[str, Any]) -> List[str]:
    """验证配置的有效性"""
    errors = []
    
    if 'project' not in config:
        errors.append("配置缺少 'project' 字段")
        return errors
    
    project = config['project']
    if 'name' not in project:
        errors.append("配置缺少 'project.name' 字段")
    
    if 'aggregates' not in config:
        errors.append("配置缺少 'aggregates' 字段")
    else:
        for i, aggregate in enumerate(config['aggregates']):
            if 'name' not in aggregate:
                errors.append(f"第 {i+1} 个聚合缺少 'name' 字段")
            
            if 'fields' not in aggregate:
                errors.append(f"聚合 '{aggregate.get('name', f'#{i+1}')}' 缺少 'fields' 字段")
            else:
                for j, field in enumerate(aggregate['fields']):
                    if 'name' not in field:
                        errors.append(f"聚合 '{aggregate.get('name', f'#{i+1}')}' 的第 {j+1} 个字段缺少 'name' 字段")
                    if 'type' not in field:
                        errors.append(f"聚合 '{aggregate.get('name', f'#{i+1}')}' 的字段 '{field.get('name', f'#{j+1}')}' 缺少 'type' 字段")
    
    return errors


def create_directory_structure(base_path: Path, structure: Dict[str, Any]) -> None:
    """创建目录结构"""
    for dir_name, sub_dirs in structure.items():
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        if isinstance(sub_dirs, dict):
            create_directory_structure(dir_path, sub_dirs)
        elif isinstance(sub_dirs, list):
            for sub_dir in sub_dirs:
                if isinstance(sub_dir, str):
                    (dir_path / sub_dir).mkdir(parents=True, exist_ok=True)
                elif isinstance(sub_dir, dict):
                    create_directory_structure(dir_path, sub_dir)

def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    # 移除或替换不安全的字符
    unsafe_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 移除空格
    filename = filename.replace(' ', '_')
    
    # 转换为小写
    filename = filename.lower()
    
    return filename


def format_code(code: str) -> str:
    """格式化代码"""
    # 简单的代码格式化
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
        
        # 处理缩进
        if line.endswith('}'):
            indent_level = max(0, indent_level - 1)
        
        formatted_line = '    ' * indent_level + line
        formatted_lines.append(formatted_line)
        
        # 增加缩进
        if line.endswith('{') or line.endswith('('):
            indent_level += 1
    
    return '\n'.join(formatted_lines)


def generate_proto_file(config: Dict[str, Any]) -> str:
    """生成proto文件内容"""
    project_name = config['project']['name']
    
    proto_template = '''syntax = "proto3";

package {project_name};

option go_package = "{project_name}/pkg/proto";

import "google/protobuf/timestamp.proto";

{messages}

{services}
'''
    
    messages = []
    services = []
    
    for aggregate in config['aggregates']:
        name = aggregate['name']
        
        # 生成消息定义
        message_fields = []
        for field in aggregate['fields']:
            proto_type = get_proto_type(field['type'])
            message_fields.append(f"    {proto_type} {field['name']} = {len(message_fields) + 1};")
        
        message = f'''
message {name.capitalize()} {{
{chr(10).join(message_fields)}
    google.protobuf.Timestamp created_at = {len(aggregate['fields']) + 1};
    google.protobuf.Timestamp updated_at = {len(aggregate['fields']) + 2};
}}'''
        messages.append(message)
        
        # 生成服务定义
        service = f'''
service {name.capitalize()}Service {{
    rpc Create{name.capitalize()}(Create{name.capitalize()}Request) returns (Create{name.capitalize()}Response);
    rpc Get{name.capitalize()}(Get{name.capitalize()}Request) returns (Get{name.capitalize()}Response);
    rpc Update{name.capitalize()}(Update{name.capitalize()}Request) returns (Update{name.capitalize()}Response);
    rpc Delete{name.capitalize()}(Delete{name.capitalize()}Request) returns (Delete{name.capitalize()}Response);
    rpc List{name.capitalize()}(List{name.capitalize()}Request) returns (List{name.capitalize()}Response);
}}'''
        services.append(service)
        
        # 生成请求响应消息
        request_messages = [
            f'''
message Create{name.capitalize()}Request {{
{chr(10).join([f"    {get_proto_type(field['type'])} {field['name']} = {i+1};" for i, field in enumerate(aggregate['fields'])])}
}}''',
            f'''
message Create{name.capitalize()}Response {{
    string message = 1;
}}''',
            f'''
message Get{name.capitalize()}Request {{
    string id = 1;
}}''',
            f'''
message Get{name.capitalize()}Response {{
    {name.capitalize()} {name.lower()} = 1;
}}''',
            f'''
message Update{name.capitalize()}Request {{
    string id = 1;
{chr(10).join([f"    {get_proto_type(field['type'])} {field['name']} = {i+2};" for i, field in enumerate(aggregate['fields'])])}
}}''',
            f'''
message Update{name.capitalize()}Response {{
    string message = 1;
}}''',
            f'''
message Delete{name.capitalize()}Request {{
    string id = 1;
}}''',
            f'''
message Delete{name.capitalize()}Response {{
    string message = 1;
}}''',
            f'''
message List{name.capitalize()}Request {{
    int32 limit = 1;
    int32 offset = 2;
}}''',
            f'''
message List{name.capitalize()}Response {{
    repeated {name.capitalize()} {name.lower()}s = 1;
}}'''
        ]
        messages.extend(request_messages)
    
    return proto_template.format(
        project_name=project_name,
        messages='\n'.join(messages),
        services='\n'.join(services)
    )