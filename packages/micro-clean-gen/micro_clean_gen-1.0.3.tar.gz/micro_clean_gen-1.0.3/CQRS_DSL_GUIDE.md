# 🏗️ CQRS DSL 完整指南

> 基于聚合根的CQRS配置DSL，支持命令、事件、读模型的统一配置

## 📋 目录

1. [快速开始](#快速开始)
2. [聚合根配置](#聚合根配置)
3. [命令定义](#命令定义)
4. [事件定义](#事件定义)
5. [读模型配置](#读模型配置)
6. [完整示例](#完整示例)
7. [最佳实践](#最佳实践)
8. [常见问题](#常见问题)

---

## 🚀 快速开始

```yaml
# cqrs-config.yaml
module: ecommerce

aggregates:
  - name: Order
    projection: true  # 启用读模型
    
    # 聚合状态（写模型）
    fields:
      - name: customerId
        type: string
      - name: items
        type: "[]OrderItem"
      - name: status
        type: string
    
    # 命令定义（业务动机）
    commands:
      - name: CreateOrder
        fields:
          - name: customerId
            type: string
            required: true
          - name: items
            type: "[]OrderItem"
            required: true
      
      - name: ConfirmOrder
        fields:
          - name: orderId
            type: string
            required: true
    
    # 事件定义（状态变化）
    events:
      - name: OrderCreated
        fields:
          - name: orderId
            type: string
          - name: customerId
            type: string
          - name: items
            type: "[]OrderItem"
          - name: createdAt
            type: time.Time
      
      - name: OrderConfirmed
        fields:
          - name: orderId
            type: string
          - name: confirmedAt
            type: time.Time
    
    # 读模型配置（查询优化）
    read_model:
      name: OrderSummary
      fields:
        - name: orderId
          type: string
        - name: customerName
          type: string
        - name: totalAmount
          type: float64
        - name: itemCount
          type: int
        - name: status
          type: string
```

---

## 🏛️ 聚合根配置

### 基础结构

```yaml
aggregates:
  - name: [聚合名称]
    projection: [true/false]    # 是否启用读模型
    
    # 聚合状态字段（写模型）
    fields:
      - name: [字段名]
        type: [类型]
        required: [true/false]   # 可选
    
    # 命令定义
    commands: [...]
    
    # 事件定义
    events: [...]
    
    # 读模型配置
    read_model: [...]
```

### 支持的字段类型

| 类型 | Go类型 | 说明 |
|------|--------|------|
| `string` | `string` | 字符串 |
| `int` | `int` | 整数 |
| `int64` | `int64` | 64位整数 |
| `float64` | `float64` | 浮点数 |
| `bool` | `bool` | 布尔值 |
| `time.Time` | `time.Time` | 时间类型 |
| `[]T` | `[]T` | 切片类型 |
| `map[string]T` | `map[string]T` | 映射类型 |

---

## ⚡ 命令定义

命令代表业务意图，驱动聚合状态变化。

### 命令结构

```yaml
commands:
  - name: [命令名称]
    description: [描述]           # 可选
    fields:
      - name: [字段名]
        type: [类型]
        required: [true/false]   # 默认为false
        validation: [规则]       # 可选，如: "email", "min:1", "max:100"
```

### 命名规范

- 使用**动词+名词**格式：如 `CreateOrder`、`CancelPayment`
- 避免CRUD命名：使用业务语言而非技术语言
- 体现业务意图：`ConfirmOrder` 而非 `UpdateOrderStatus`

### 示例

```yaml
commands:
  - name: PlaceOrder
    description: "客户下单"
    fields:
      - name: customerId
        type: string
        required: true
      - name: items
        type: "[]OrderItem"
        required: true
      - name: shippingAddress
        type: Address
        required: true
  
  - name: CancelOrder
    description: "取消订单"
    fields:
      - name: orderId
        type: string
        required: true
      - name: reason
        type: string
        required: false
```

---

## 📊 事件定义

事件表示已发生的事实，是聚合间通信的媒介。

### 事件结构

```yaml
events:
  - name: [事件名称]
    description: [描述]           # 可选
    fields:
      - name: [字段名]
        type: [类型]
```

### 命名规范

- 使用**过去时态**：如 `OrderCreated`、`PaymentConfirmed`
- 体现事实：`OrderShipped` 而非 `OrderShip`
- 保持简洁：事件应该只包含必要信息

### 事件类型

| 事件类型 | 示例 | 说明 |
|----------|------|------|
| 创建事件 | `OrderCreated` | 聚合创建时发出 |
| 状态事件 | `OrderConfirmed` | 状态变化时发出 |
| 删除事件 | `OrderCancelled` | 聚合删除时发出 |

### 示例

```yaml
events:
  - name: OrderPlaced
    description: "订单已创建"
    fields:
      - name: orderId
        type: string
      - name: customerId
        type: string
      - name: items
        type: "[]OrderItem"
      - name: totalAmount
        type: float64
      - name: placedAt
        type: time.Time
  
  - name: OrderShipped
    description: "订单已发货"
    fields:
      - name: orderId
        type: string
      - name: trackingNumber
        type: string
      - name: shippedAt
        type: time.Time
```

---

## 📖 读模型配置

读模型优化查询性能，支持多种查询场景。

### 读模型结构

```yaml
read_model:
  name: [读模型名称]
  description: [描述]           # 可选
  fields:
    - name: [字段名]
      type: [类型]
      source: [来源]            # 可选，说明数据来源
  
  # 查询优化
  indexes:
    - [字段1, 字段2]            # 复合索引
  
  # 缓存配置
  cache:
    ttl: [时长]                # 如: "5m", "1h"
```

### 读模型设计原则

1. **去规范化**：为了查询性能，可以冗余存储数据
2. **查询导向**：根据实际查询需求设计字段
3. **版本演进**：支持字段添加，避免破坏性变更

### 示例

```yaml
read_model:
  name: OrderListView
  description: "订单列表查询视图"
  fields:
    - name: orderId
      type: string
    - name: customerName      # 去规范化存储
      type: string
    - name: totalAmount
      type: float64
    - name: status
      type: string
    - name: createdAt
      type: time.Time
  
  indexes:
    - [customerId, createdAt]
    - [status]
```

---

## 🎯 完整示例

### 电商系统 - 订单聚合

```yaml
module: ecommerce

description: "电商订单系统CQRS配置"

aggregates:
  - name: Order
    projection: true
    
    # 聚合状态
    fields:
      - name: id
        type: string
      - name: customerId
        type: string
      - name: items
        type: "[]OrderItem"
      - name: shippingAddress
        type: Address
      - name: status
        type: string
      - name: totalAmount
        type: float64
    
    # 命令
    commands:
      - name: CreateOrder
        fields:
          - name: customerId
            type: string
            required: true
          - name: items
            type: "[]OrderItem"
            required: true
          - name: shippingAddress
            type: Address
            required: true
      
      - name: ConfirmOrder
        fields:
          - name: orderId
            type: string
            required: true
      
      - name: CancelOrder
        fields:
          - name: orderId
            type: string
            required: true
          - name: reason
            type: string
    
    # 事件
    events:
      - name: OrderCreated
        fields:
          - name: orderId
            type: string
          - name: customerId
            type: string
          - name: items
            type: "[]OrderItem"
          - name: shippingAddress
            type: Address
          - name: totalAmount
            type: float64
          - name: createdAt
            type: time.Time
      
      - name: OrderConfirmed
        fields:
          - name: orderId
            type: string
          - name: confirmedAt
            type: time.Time
      
      - name: OrderCancelled
        fields:
          - name: orderId
            type: string
          - name: reason
            type: string
          - name: cancelledAt
            type: time.Time
    
    # 读模型
    read_model:
      name: OrderSummary
      fields:
        - name: orderId
          type: string
        - name: customerName
          type: string
        - name: itemCount
          type: int
        - name: totalAmount
          type: float64
        - name: status
          type: string
        - name: createdAt
          type: time.Time
```

---

## 🏆 最佳实践

### 1. 命令设计
- **单一职责**：每个命令只做一件事
- **业务语言**：使用领域术语，避免技术术语
- **验证前置**：在命令层面进行输入验证

### 2. 事件设计
- **不可变**：事件一旦发出，不可更改
- **自足性**：事件包含所有必要信息
- **版本化**：支持事件版本演进

### 3. 读模型设计
- **查询驱动**：根据UI/查询需求设计
- **去规范化**：适当冗余以提升性能
- **渐进演进**：支持字段添加，避免破坏

### 4. 聚合边界
- **一致性边界**：聚合内保证强一致性
- **业务边界**：基于业务规则划分
- **大小适中**：避免过大或过小的聚合

---

## ❓ 常见问题

### Q1: 什么时候需要读模型？

**A**: 当以下情况时：
- 需要复杂查询或报表
- 查询性能成为瓶颈
- 需要不同数据视图
- 需要缓存优化

### Q2: 命令和事件的区别？

**A**: 
- **命令** = 业务意图（可能失败）
- **事件** = 已发生事实（不会失败）

### Q3: 如何处理事件版本演进？

**A**: 
- 事件版本化：`OrderCreated_v1`, `OrderCreated_v2`
- 向上兼容：新事件处理器处理旧事件
- 迁移策略：逐步迁移，支持回滚

### Q4: 读模型如何保持同步？

**A**: 
- **最终一致性**：接受短暂不一致
- **重试机制**：处理网络/系统故障
- **监控告警**：及时发现同步延迟

---

## 🚀 使用命令

```bash
# 生成完整CQRS代码
micro-gen cqrs --config cqrs-config.yaml

# 查看帮助
micro-gen cqrs --help
```

---

**记住**：CQRS不是银弹，只有在**读写差异大**、**查询复杂**、**性能要求高**的场景下才推荐使用！