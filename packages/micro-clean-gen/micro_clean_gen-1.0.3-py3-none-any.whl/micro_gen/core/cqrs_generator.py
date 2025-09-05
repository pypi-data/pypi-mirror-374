"""
投影机制生成器 - 基于整洁架构的读模型投影（模板化版本）
"""

import os
from typing import Dict, List, Any
from .base_generator import BaseGenerator


class ProjectionGenerator(BaseGenerator):
    """基于整洁架构的读模型投影代码生成器 - 使用模板"""
    
    def __init__(self, module_name: str, config: Dict[str, Any]):
        super().__init__(module_name, config)
        # 整洁架构目录结构
        self.entity_dir = "internal/entity/projection"
        self.usecase_dir = "internal/usecase/projection"
        self.adapter_dir = "adapter/persistence"
        self.processor_dir = "adapter/projection"
        self.cmd_dir = "cmd"
    
    def generate(self) -> List[str]:
        """生成整洁架构的投影代码"""
        generated_files = []
        
        # 1. 生成核心实体
        entity_file = self._generate_entity()
        generated_files.append(entity_file)
        
        # 2. 生成内存存储适配器
        adapter_file = self._generate_adapter()
        generated_files.append(adapter_file)
        
        # 3. 为每个启用了投影的聚合生成代码
        for aggregate in self.config.get('aggregates', []):
            if aggregate.get('projection', False):
                files = self._generate_aggregate_projection(aggregate)
                generated_files.extend(files)
        
        # 4. 生成使用示例
        example_file = self._generate_example()
        generated_files.append(example_file)
        
        return generated_files
    
    def _generate_entity(self) -> str:
        """生成核心实体"""
        output_path = os.path.join(self.output_dir, self.entity_dir, "read_model.go")
        template_path = self._get_template_path("entity_read_model.go.tmpl")
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)

        # 同时生成query.go
        query_path = os.path.join(self.output_dir, self.entity_dir, "query.go")
        query_template = self._get_template_path("query.go.tmpl")
        
        query_content = self.render_template(query_template, {
            'ModuleName': self.module_name
        })
        
        with open(query_path, 'w') as f:
            f.write(query_content)
        
        return output_path
    
    def _generate_adapter(self) -> str:
        """生成内存存储适配器"""
        output_path = os.path.join(self.output_dir, self.adapter_dir, "memory_read_model_repository.go")
        template_path = self._get_template_path("memory_repository.go.tmpl")
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_aggregate_projection(self, aggregate: Dict[str, Any]) -> List[str]:
        """为聚合生成整洁架构的投影代码"""
        files = []
        
        aggregate_name = aggregate['name']
        
        # 1. 生成特定聚合的读模型实体
        model_file = self._generate_aggregate_model(aggregate)
        files.append(model_file)
        
        # 2. 生成用例层服务
        service_file = self._generate_service(aggregate)
        files.append(service_file)
        
        # 3. 生成投影处理器
        processor_file = self._generate_processor(aggregate)
        files.append(processor_file)
        
        return files
    
    def _generate_aggregate_model(self, aggregate: Dict[str, Any]) -> str:
        """生成特定聚合的读模型实体"""
        aggregate_name = aggregate['name']
        aggregate_lower = aggregate_name.lower()
        
        output_path = os.path.join(self.output_dir, self.entity_dir, f"{aggregate_lower}_read_model.go")
        template_path = self._get_template_path("aggregate_read_model.go.tmpl")
        
        # 生成业务字段
        fields = []
        for field in aggregate.get('fields', []):
            field_name = field['name']
            field_type = self._go_type(field['type'])
            json_tag = field_name.lower()
            
            # 跳过内部字段
            if field_name.lower() not in ['events', 'version', 'id']:
                fields.append({
                    'name': field_name.capitalize(),
                    'type': field_type,
                    'json': json_tag
                })
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name,
            'AggregateName': aggregate_name,
            'AggregateLower': aggregate_lower,
            'Fields': fields
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_service(self, aggregate: Dict[str, Any]) -> str:
        """生成用例层服务"""
        aggregate_name = aggregate['name']
        aggregate_lower = aggregate_name.lower()
        
        output_path = os.path.join(self.output_dir, self.usecase_dir, f"{aggregate_lower}_projection_service.go")
        template_path = self._get_template_path("projection_service.go.tmpl")
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name,
            'AggregateName': aggregate_name,
            'AggregateLower': aggregate_lower
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_processor(self, aggregate: Dict[str, Any]) -> str:
        """生成投影处理器"""
        aggregate_name = aggregate['name']
        aggregate_lower = aggregate_name.lower()
        
        output_path = os.path.join(self.output_dir, self.processor_dir, f"{aggregate_lower}_projection_processor.go")
        template_path = self._get_template_path("projection_processor.go.tmpl")
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name,
            'AggregateName': aggregate_name,
            'AggregateLower': aggregate_lower
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_example(self) -> str:
        """生成使用示例"""
        output_path = os.path.join(self.output_dir, self.cmd_dir, "projection_example.go")
        template_path = self._get_template_path("projection_example.go.tmpl")
        
        content = self.render_template(template_path, {
            'ModuleName': self.module_name
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _get_template_path(self, template_name: str) -> str:
        """获取模板文件路径"""
        return os.path.join(
            os.path.dirname(__file__),
            'templates',
            'projection',
            template_name
        )
    
    def _go_type(self, type_str: str) -> str:
        """将类型映射到Go类型"""
        type_mapping = {
            'string': 'string',
            'int': 'int',
            'int64': 'int64',
            'float64': 'float64',
            'bool': 'bool',
            'time': 'time.Time',
            'uuid': 'string',
        }
        return type_mapping.get(type_str, 'string')
    
    def get_instructions(self) -> str:
        """获取使用说明"""
        return """
🏗️ 整洁架构投影系统已生成完成！

📁 整洁架构目录结构：
├── internal/entity/projection/           # 实体层（核心业务逻辑）
│   ├── read_model.go                    # 通用读模型实体
│   └── {aggregate}_read_model.go        # 特定聚合读模型
├── internal/usecase/projection/          # 用例层（业务逻辑）
│   ├── {aggregate}_projection_service.go # 投影业务服务
├── adapter/persistence/                  # 适配器层（基础设施）
│   └── memory_read_model_repository.go  # 内存存储实现
├── adapter/projection/                   # 适配器层（事件处理）
│   └── {aggregate}_projection_processor.go # 事件处理器
└── cmd/projection_example.go            # 使用示例

🎯 架构原则：
- entity/     : 核心业务实体和值对象
- usecase/    : 业务逻辑和应用服务
- adapter/    : 基础设施和外部接口

🚀 使用步骤：
1. 在聚合配置中设置 "projection: true"
2. 创建聚合时会自动生成投影相关代码
3. 将投影处理器注册到事件总线
4. 通过用例层服务查询读模型

💡 设计亮点：
- 符合整洁架构（Clean Architecture）
- 依赖倒置：业务逻辑不依赖基础设施
- 可测试：用例层可独立单元测试
- 可扩展：轻松切换存储实现
"""


"""
CQRS 生成器 - 基于整洁架构的命令查询职责分离系统
支持命令、事件、聚合、读模型的统一配置与代码生成
"""

import os
from typing import Dict, List, Any
from .base_generator import BaseGenerator


class CQRSGenerator(BaseGenerator):
    """CQRS代码生成器 - 支持完整的CQRS架构模式"""
    
    def __init__(self, module_name: str, config: Dict[str, Any]):
        super().__init__(module_name, config)
        # 整洁架构目录结构
        self.entity_dir = "internal/entity"
        self.usecase_dir = "internal/usecase"
        self.adapter_dir = "adapter"
        self.cmd_dir = "cmd"
    
    def generate(self, config_path: str) -> Dict[str, Any]:
        """根据配置生成CQRS代码
        
        配置示例:
        ```yaml
        aggregates:
          - name: User
            fields:
              - name: username
                type: string
                json: username
              - name: email
                type: string
                json: email
            commands:
              - name: CreateUser
                fields:
                  - name: username
                    type: string
                    json: username
                  - name: email
                    type: string
                    json: email
              - name: UpdateUser
                fields:
                  - name: username
                    type: string
                    json: username
                  - name: email
                    type: string
                    json: email
            events:
              - name: UserCreated
                fields:
                  - name: username
                    type: string
                    json: username
                  - name: email
                    type: string
                    json: email
              - name: UserUpdated
                fields:
                  - name: username
                    type: string
                    json: username
                  - name: email
                    type: string
                    json: email
            readModel:
              name: UserReadModel
              fields:
                - name: username
                  type: string
                  json: username
                - name: email
                  type: string
                  json: email
        ```
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            results = {
                'generated_files': [],
                'errors': []
            }
            
            # 处理每个聚合
            for aggregate_config in config.get('aggregates', []):
                try:
                    files = self._generate_aggregate_cqrs(aggregate_config)
                    results['generated_files'].extend(files)
                except Exception as e:
                    results['errors'].append(f"Error generating aggregate {aggregate_config.get('name', 'unknown')}: {str(e)}")
            
            # 生成示例文件
            try:
                example_file = self._generate_example()
                results['generated_files'].append(example_file)
            except Exception as e:
                results['errors'].append(f"Error generating example: {str(e)}")
                
            return results
            
        except Exception as e:
            return {
                'generated_files': [],
                'errors': [str(e)]
            }

    def _generate_aggregate_cqrs(self, config: Dict[str, Any]) -> List[str]:
        """为单个聚合生成完整的CQRS代码"""
        files = []
        
        # 创建聚合目录
        aggregate_name = config['name']
        aggregate_dir = os.path.join(self.output_dir, aggregate_name.lower())
        
        # 创建子目录
        dirs = [
            os.path.join(aggregate_dir, "entity"),
            os.path.join(aggregate_dir, "command"),
            os.path.join(aggregate_dir, "event"),
            os.path.join(aggregate_dir, "usecase"),
            os.path.join(aggregate_dir, "projection"),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        # 生成各个组件
        self._generate_aggregate_entity(config, aggregate_dir)
        files.append(os.path.join(aggregate_dir, "entity", f"{config['name'].lower()}.go"))
        
        self._generate_command(config, aggregate_dir)
        for command in config.get('commands', []):
            files.append(os.path.join(aggregate_dir, "command", f"{command['name'].lower()}_command.go"))
        
        self._generate_event(config, aggregate_dir)
        for event in config.get('events', []):
            files.append(os.path.join(aggregate_dir, "event", f"{event['name'].lower()}_event.go"))
        
        self._generate_command_handler(config, aggregate_dir)
        for command in config.get('commands', []):
            files.append(os.path.join(aggregate_dir, "usecase", f"{command['name'].lower()}_handler.go"))
        
        self._generate_read_model(config, aggregate_dir)
        if 'readModel' in config:
            files.append(os.path.join(aggregate_dir, "projection", f"{config['name'].lower()}_read_model.go"))
        
        self._generate_projection_processor(config, aggregate_dir)
        if 'readModel' in config:
            files.append(os.path.join(aggregate_dir, "projection", f"{config['name'].lower()}_projection_processor.go"))
        
        return files

    def _generate_example(self) -> str:
        """生成CQRS使用示例"""
        output_path = os.path.join(self.output_dir, "cmd", "cqrs_example.go")
        template_path = self._get_template_path("cqrs_example.go.tmpl")
        
        template = self.template_loader.load_template(template_path)
        content = template.render(ModuleName=self.module_name)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self._write_file(output_path, content)
        
        return output_path

    def _write_file(self, file_path: str, content: str):
        """写入文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

    def _generate_command(self, config, output_dir):
        """生成命令对象"""
        for command in config['commands']:
            template_path = self._get_template_path("command.go.tmpl")
            output_path = os.path.join(output_dir, "command", f"{command['name'].lower()}_command.go")
            
            template = self.template_loader.load_template(template_path)
            content = template.render(
                AggregateLower=config['aggregate']['name'].lower(),
                CommandName=command['name'],
                Fields=command['fields']
            )
            
            self._write_file(output_path, content)

    def _generate_event(self, config, output_dir):
        """生成事件对象"""
        for event in config['events']:
            template_path = self._get_template_path("event.go.tmpl")
            output_path = os.path.join(output_dir, "event", f"{event['name'].lower()}_event.go")
            
            template = self.template_loader.load_template(template_path)
            content = template.render(
                ModuleName=self.module_name,
                AggregateLower=config['aggregate']['name'].lower(),
                AggregateName=config['aggregate']['name'],
                EventName=event['name'],
                Fields=event['fields']
            )
            
            self._write_file(output_path, content)

    def _generate_command_handler(self, config, output_dir):
        """生成命令处理器"""
        for command in config['commands']:
            template_path = self._get_template_path("command_handler.go.tmpl")
            output_path = os.path.join(output_dir, "usecase", f"{command['name'].lower()}_handler.go")
            
            template = self.template_loader.load_template(template_path)
            content = template.render(
                ModuleName=self.module_name,
                AggregateLower=config['aggregate']['name'].lower(),
                CommandName=command['name']
            )
            
            self._write_file(output_path, content)

    def _generate_read_model(self, config, output_dir):
        """生成读模型"""
        if 'readModel' not in config:
            return
            
        template_path = self._get_template_path("read_model.go.tmpl")
        output_path = os.path.join(output_dir, "projection", f"{config['aggregate']['name'].lower()}_read_model.go")
        
        template = self.template_loader.load_template(template_path)
        content = template.render(
            ModuleName=self.module_name,
            AggregateLower=config['aggregate']['name'].lower(),
            AggregateName=config['aggregate']['name'],
            Fields=config['readModel']['fields']
        )
        
        self._write_file(output_path, content)

    def _generate_projection_processor(self, config, output_dir):
        """生成投影处理器"""
        if 'readModel' not in config:
            return
            
        template_path = self._get_template_path("projection_processor.go.tmpl")
        output_path = os.path.join(output_dir, "projection", f"{config['aggregate']['name'].lower()}_projection_processor.go")
        
        template = self.template_loader.load_template(template_path)
        content = template.render(
            ModuleName=self.module_name,
            AggregateLower=config['aggregate']['name'].lower(),
            AggregateName=config['aggregate']['name']
        )
        
        self._write_file(output_path, content)
    
    def _go_type(self, type_str: str) -> str:
        """将类型映射到Go类型"""
        type_mapping = {
            'string': 'string',
            'int': 'int',
            'int64': 'int64',
            'float64': 'float64',
            'bool': 'bool',
            'time': 'time.Time',
            'time.Time': 'time.Time',
            'uuid': 'string',
        }
        return type_mapping.get(type_str, 'string')
    
    def get_instructions(self) -> str:
        """获取使用说明"""
        return """
🏗️ CQRS系统已生成完成！

📁 整洁架构目录结构：
├── internal/entity/               # 实体层（核心业务）
│   ├── {aggregate}/              # 聚合根实体
│   ├── {aggregate}_event.go       # 事件定义
│   └── projection/               # 读模型实体
├── internal/usecase/             # 用例层（业务逻辑）
│   ├── {aggregate}/              # 聚合用例
│   │   ├── {command}_command.go  # 命令处理器
│   │   └── {aggregate}_query_service.go  # 查询服务
├── adapter/                      # 适配器层（基础设施）
└── cmd/cqrs_example.go          # 使用示例

🎯 架构原则：
- entity/     : 核心业务实体和值对象
- usecase/    : 业务逻辑和应用服务
- adapter/    : 基础设施和外部接口

🚀 使用步骤：
1. 创建CQRS配置文件
2. 运行: micro-gen cqrs --config your-config.yaml
3. 查看生成的代码结构
4. 实现业务逻辑细节

💡 设计亮点：
- 完整的CQRS模式支持
- 命令、事件、读模型统一配置
- 整洁架构，依赖倒置
- 渐进式演进支持
"""