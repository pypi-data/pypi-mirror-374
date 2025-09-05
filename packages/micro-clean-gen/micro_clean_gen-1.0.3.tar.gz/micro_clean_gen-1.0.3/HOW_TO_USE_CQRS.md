# CQRS 生成器使用指南

## 快速开始

### 1. 创建CQRS配置

创建一个YAML配置文件（例如：`user_cqrs.yaml`）：

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
            required: true
          - name: email
            type: string
            json: email
            required: true
    events:
      - name: UserCreated
        fields:
          - name: userId
            type: string
            json: user_id
          - name: username
            type: string
            json: username
          - name: email
            type: string
            json: email
    readModel:
      name: UserReadModel
      fields:
        - name: userId
          type: string
          json: user_id
        - name: username
          type: string
          json: username
        - name: email
          type: string
          json: email
```

### 2. 运行CQRS生成器

```python
from micro_gen.core.cqrs_generator import CQRSGenerator

# 初始化生成器
generator = CQRSGenerator(
    module_name="your-app",
    output_dir="./internal"
)

# 生成CQRS代码
result = generator.generate("user_cqrs.yaml")

# 检查结果
if result['errors']:
    for error in result['errors']:
        print(f"错误: {error}")
else:
    print(f"成功生成 {len(result['generated_files'])} 个文件")
```

### 3. 生成的目录结构

```
internal/
├── user/
│   ├── entity/
│   │   └── user.go              # 聚合根实体
│   ├── command/
│   │   └── createuser_command.go # 命令对象
│   ├── event/
│   │   └── usercreated_event.go  # 事件对象
│   ├── usecase/
│   │   └── createuser_handler.go # 命令处理器
│   └── projection/
│       ├── user_read_model.go    # 读模型
│       └── user_projection_processor.go  # 投影处理器
└── cmd/
    └── cqrs_example.go           # 使用示例
```

## 配置详解

### 聚合配置

每个聚合配置包含以下部分：

- **name**: 聚合名称（必须）
- **fields**: 聚合字段定义
- **commands**: 命令定义
- **events**: 事件定义
- **readModel**: 读模型定义（可选）

### 字段类型映射

| YAML类型 | Go类型 |
|---------|--------|
| string  | string |
| int     | int    |
| float64 | float64|
| bool    | bool   |
| time.Time | time.Time |

## 使用示例

### 1. 创建命令处理器

```go
// 在您的服务中
func (s *UserService) CreateUser(ctx context.Context, cmd *CreateUserCommand) error {
    handler := user.NewCreateUserHandler(s.repository, s.eventBus)
    return handler.Handle(ctx, cmd)
}
```

### 2. 注册事件处理器

```go
// 在初始化时
func init() {
    projectionProcessor := user.NewUserProjectionProcessor(projectionRepo)
    eventBus.RegisterHandler("UserCreated", projectionProcessor)
}
```

### 3. 查询读模型

```go
// 查询用户
query := projection.NewQuery().
    WithFilter("username", "john_doe").
    WithLimit(10)

users, err := projectionRepo.FindByQuery(ctx, query)
```

## 最佳实践

### 1. 命名规范

- 聚合名称使用帕斯卡命名（PascalCase）
- 命令名称以"Command"结尾
- 事件名称以"Event"结尾
- 读模型名称以"ReadModel"结尾

### 2. 目录组织

每个聚合一个目录，包含：
- entity/ - 聚合根和值对象
- command/ - 命令定义
- event/ - 事件定义
- usecase/ - 业务逻辑
- projection/ - 读模型和投影

### 3. 事件溯源

- 所有状态变更通过事件记录
- 读模型通过事件投影构建
- 支持事件重放恢复状态

## 常见问题

### Q: 如何添加新的聚合？
A: 在YAML配置中添加新的聚合定义，然后重新运行生成器。

### Q: 如何修改生成的代码？
A: 建议直接修改模板文件（在templates/cqrs/目录下），然后重新生成。

### Q: 支持哪些存储后端？
A: 默认提供内存存储实现，可以通过实现接口支持其他存储。

### Q: 如何处理复杂业务逻辑？
A: 在命令处理器中实现业务规则，保持聚合根简洁。

## 高级配置

### 事件版本控制

```yaml
events:
  - name: UserCreated
    version: 1
    fields:
      - name: userId
        type: string
        json: user_id
```

### 字段验证

```yaml
fields:
  - name: email
    type: string
    json: email
    validation:
      required: true
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
```

### 投影策略

```yaml
readModel:
  name: UserReadModel
  projection:
    strategy: "event_sourcing"
    rebuild: true
  fields:
    - name: userId
      type: string
      json: user_id
```