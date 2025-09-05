# 🔧 一键CRUD生成指南

## 项目简介

一键CRUD生成器能够根据简单的实体定义，自动生成完整的**增删改查**功能代码，包括实体、仓库、REST API Handler、路由和测试。

## 🚀 快速开始

### 方式1：配置文件模式（推荐）

创建配置文件 `crud-config.yaml`：
```yaml
entities:
  - name: User
    table: users
    description: "系统用户"
    fields:
      - name: username
        type: string
        required: true
        unique: true
        description: "用户名"
      - name: email
        type: string
        required: true
        unique: true
        description: "邮箱"
      - name: age
        type: int
        required: false
        description: "年龄"
```

生成CRUD：
```bash
micro-gen crud --config ./crud-config.yaml
```

### 方式2：简单模式（快速）

一行命令生成：
```bash
# 生成用户CRUD
micro-gen crud --entity user --fields "username:string,email:string,age:int"

# 生成产品CRUD
micro-gen crud --entity product --fields "name:string,price:float,stock:int"

# 指定项目路径
micro-gen crud --path ./my-project --entity order --fields "user_id:uint,total:float,status:string"
```

## 📋 生成的代码结构

```
internal/
├── entity/
│   └── user.go          # 实体定义
├── repo/
│   └── user_repo.go     # 数据仓库
adapter/
└── handler/
    └── user_handler.go  # REST API处理器
pkg/
└── http/
    └── user_routes.go   # 路由注册
test/
└── user_test.go         # 单元测试
```

## 🎯 功能特性

### ✅ 自动生成的功能
- **实体定义** - GORM模型 + JSON标签
- **数据仓库** - 完整的CRUD操作
- **REST API** - 标准的RESTful接口
- **路由注册** - Gin路由自动注册
- **Swagger文档** - API文档注释
- **单元测试** - 测试模板
- **分页查询** - 内置分页支持
- **错误处理** - 统一的错误响应

### 🛠️ 支持的字段类型
```bash
# 基本类型
string      # 字符串
int         # 整数
int64       # 长整数
float64     # 浮点数
bool        # 布尔值
time.Time   # 时间类型

# 指针类型（可选字段）
*string     # 可选字符串
*int        # 可选整数
*time.Time  # 可选时间
```

## 📖 使用示例

### 示例1：用户管理
```bash
micro-gen crud --entity user --fields "username:string,email:string,password:string,avatar:string,status:int"
```

生成后自动拥有：
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users` - 用户列表（分页）
- `GET /api/v1/users/:id` - 用户详情
- `PUT /api/v1/users/:id` - 更新用户
- `DELETE /api/v1/users/:id` - 删除用户

### 示例2：博客系统
配置文件模式：
```yaml
entities:
  - name: Post
    table: posts
    description: "博客文章"
    fields:
      - name: title
        type: string
        required: true
        description: "文章标题"
      - name: content
        type: string
        required: true
        description: "文章内容"
      - name: author_id
        type: uint
        required: true
        description: "作者ID"
      - name: status
        type: int
        default: 1
        description: "发布状态"
```

### 示例3：电商系统
```bash
# 产品
micro-gen crud --entity product --fields "name:string,description:string,price:float,stock:int,category_id:uint"

# 订单
micro-gen crud --entity order --fields "user_id:uint,total_amount:float,status:string,payment_method:string"

# 订单项
micro-gen crud --entity order_item --fields "order_id:uint,product_id:uint,quantity:int,price:float"
```

## 🔍 配置文件详解

### 完整配置示例
```yaml
entities:
  - name: User
    table: users  # 数据库表名
    description: "用户实体"
    soft_delete: true      # 软删除
    timestamps: true       # 自动时间戳
    fields:
      - name: id
        type: uint
        description: "主键ID"
      - name: username
        type: string
        required: true     # 必填
        unique: true       # 唯一索引
        description: "用户名"
      - name: email
        type: string
        required: true
        unique: true
        description: "邮箱地址"
      - name: age
        type: int
        required: false    # 可选
        default: 0
        description: "年龄"
      - name: birth_date
        type: "*time.Time" # 可选时间
        required: false
        description: "生日"
      - name: is_active
        type: bool
        default: true
        description: "是否激活"
```

### 字段配置选项
```yaml
fields:
  - name: field_name
    type: string              # 数据类型
    required: true/false      # 是否必填
    unique: true/false        # 是否唯一
    index: true/false         # 是否索引
    default: value           # 默认值
    description: "描述"       # 字段描述
```

## 🎯 使用技巧

### 1. 组合使用
```bash
# 先初始化项目
micro-gen init --name blog-system

# 再生成CRUD
micro-gen crud --config ./blog-entities.yaml

# 最后部署
micro-gen deploy --name blog-system
```

### 2. 增量开发
```bash
# 先生成用户模块
micro-gen crud --entity user --fields "name:string,email:string"

# 后续添加文章模块
micro-gen crud --entity post --fields "title:string,content:string,user_id:uint"
```

### 3. 字段命名规范
```bash
# 推荐命名
user_id:uint        # 外键
created_at:time.Time # 时间戳
is_deleted:bool      # 状态字段
avatar_url:string    # URL字段
```

## 🚀 快速开发流程

### 完整示例：博客系统

1. **创建项目**
```bash
micro-gen init --name blog-system
cd blog-system
```

2. **创建配置文件** `blog-crud.yaml`：
```yaml
entities:
  - name: User
    table: users
    fields:
      - name: username
        type: string
        required: true
        unique: true
      - name: email
        type: string
        required: true
        unique: true
  - name: Post
    table: posts
    fields:
      - name: title
        type: string
        required: true
      - name: content
        type: string
        required: true
      - name: user_id
        type: uint
        required: true
```

3. **生成CRUD**
```bash
micro-gen crud --config ./blog-crud.yaml
```

4. **启动服务**
```bash
make run
# 或
make deploy-local
```

5. **测试API**
```bash
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com"}'
```

## 📊 生成的API端点

每个实体自动生成5个标准REST端点：

| 方法 | 路径 | 描述 |
|---|---|---|
| POST | /api/v1/{entities} | 创建记录 |
| GET | /api/v1/{entities} | 分页列表 |
| GET | /api/v1/{entities}/:id | 详情查询 |
| PUT | /api/v1/{entities}/:id | 更新记录 |
| DELETE | /api/v1/{entities}/:id | 删除记录 |

## 🔧 自定义扩展

### 1. 添加自定义验证
在生成的handler中添加：
```go
// 在Create方法中添加验证
if user.Username == "" {
    c.JSON(http.StatusBadRequest, gin.H{"error": "用户名不能为空"})
    return
}
```

### 2. 添加业务逻辑
在仓库层添加：
```go
// 在user_repo.go中添加自定义查询
func (r *UserRepository) FindByEmail(ctx context.Context, email string) (*entity.User, error) {
    var user entity.User
    err := r.db.WithContext(ctx).Where("email = ?", email).First(&user).Error
    return &user, err
}
```

### 3. 添加关联查询
```go
// 在查询时预加载关联
func (r *PostRepository) ListWithUser(ctx context.Context, limit, offset int) ([]*entity.Post, error) {
    var posts []*entity.Post
    err := r.db.WithContext(ctx).Preload("User").Limit(limit).Offset(offset).Find(&posts).Error
    return posts, err
}
```

## 🎉 总结

一键CRUD生成器让你：
- **从0到完整API** 只需几分钟
- **告别重复劳动** 专注业务逻辑
- **标准化代码** 统一项目规范
- **包含测试** 保证代码质量

**最大节省时间，最小技术含量，最高开发效率！** 🚀