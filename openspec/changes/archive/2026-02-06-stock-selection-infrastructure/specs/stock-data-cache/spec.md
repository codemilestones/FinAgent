## ADDED Requirements

### Requirement: 缓存抽象接口
系统 MUST 定义一个缓存抽象接口，支持以下操作：
- `get(key: str) -> Optional[Any]`: 从缓存获取数据
- `set(key: str, value: Any, ttl: int)`: 设置缓存数据
- `delete(key: str)`: 删除缓存数据
- `clear()`: 清空所有缓存
- `exists(key: str) -> bool`: 检查缓存是否存在

#### Scenario: 缓存命中
- **WHEN** 请求的数据存在于缓存中且未过期
- **THEN** MUST 直接从缓存返回数据
- **AND** MUST 不调用数据源 API

#### Scenario: 缓存未命中
- **WHEN** 请求的数据不存在于缓存或已过期
- **THEN** MUST 返回 None
- **AND** 上层逻辑 MUST 调用数据源获取数据

### Requirement: SQLite 缓存实现
系统 MUST 实现 SQLite 作为缓存存储：
- 数据库文件默认位置：`~/.finagent/cache.db`
- 支持缓存键的自动过期（TTL）
- 支持批量操作
- 线程安全

#### Scenario: 初始化缓存数据库
- **WHEN** 第一次使用缓存
- **THEN** 系统 MUST 自动创建缓存数据库和必要的表结构
- **AND** 表结构 MUST 包含：key、value、expire_time 字段

#### Scenario: 设置带 TTL 的缓存
- **WHEN** 调用 `set("stock:sh.600000:info", data, ttl=3600)`
- **THEN** 数据 MUST 被存储到 SQLite
- **AND** expire_time MUST 设置为当前时间 + 3600 秒
- **AND** 3600 秒后该数据 MUST 被视为过期

#### Scenario: 获取过期缓存
- **WHEN** 调用 `get("stock:sh.600000:info")` 且缓存已过期
- **THEN** MUST 返回 None
- **AND** 数据库中该记录 MUST 被自动删除

### Requirement: 缓存键命名规范
系统 MUST 使用统一的缓存键命名规范，格式为：
- 股票基本信息：`stock:{code}:info`
- 历史行情数据：`stock:{code}:history:{start_date}:{end_date}:{frequency}`
- 分红数据：`stock:{code}:dividend`
- 财务数据：`stock:{code}:financial:{year}:{quarter}`

#### Scenario: 生成缓存键
- **WHEN** 缓存 sh.600000 的基本信息
- **THEN** 缓存键 MUST 为 `stock:sh.600000:info`

#### Scenario: 生成历史数据缓存键
- **WHEN** 缓存 sh.600000 的 2023 年日 K 线数据
- **THEN** 缓存键 MUST 为 `stock:sh.600000:history:2023-01-01:2023-12-31:d`

### Requirement: 默认 TTL 配置
系统 MUST 为不同类型的数据设置默认缓存有效期：
- 股票基本信息：2592000 秒（30 天）
- 历史行情数据：604800 秒（7 天）
- 分红数据：86400 秒（1 天）
- 财务数据：86400 秒（1 天）

#### Scenario: 使用默认 TTL
- **WHEN** 缓存股票基本信息且未指定 TTL
- **THEN** MUST 使用默认 TTL 2592000 秒

#### Scenario: 覆盖默认 TTL
- **WHEN** 缓存时显式指定 TTL 参数
- **THEN** MUST 使用指定的 TTL 值覆盖默认值

### Requirement: 缓存统计
系统 MUST 提供缓存统计功能：
- 命中次数
- 未命中次数
- 命中率
- 缓存大小

#### Scenario: 获取缓存统计
- **WHEN** 调用 `get_stats()`
- **THEN** MUST 返回包含命中次数、未命中次数、命中率等信息的字典

#### Scenario: 重置缓存统计
- **WHEN** 调用 `reset_stats()`
- **THEN** 命中次数和未命中次数 MUST 重置为 0

### Requirement: 缓存管理
系统 MUST 提供缓存管理功能：
- 手动刷新指定缓存
- 清空所有缓存
- 清空过期缓存

#### Scenario: 刷新指定股票缓存
- **WHEN** 调用 `invalidate("stock:sh.600000:*")`
- **THEN** 所有匹配的缓存 MUST 被删除
- **AND** 支持通配符匹配

#### Scenario: 清空过期缓存
- **WHEN** 调用 `cleanup_expired()`
- **THEN** 所有已过期的缓存记录 MUST 被删除
- **AND** 数据库大小 MUST 减小

### Requirement: 缓存序列化
系统 MUST 支持复杂数据类型的序列化和反序列化：
- pandas.DataFrame
- 自定义数据类（StockInfo 等）
- 基本数据类型（dict、list、str 等）

#### Scenario: 缓存 DataFrame
- **WHEN** 缓存 pandas.DataFrame 对象
- **THEN** MUST 自动序列化为 JSON 或其他格式存储
- **AND** 读取时 MUST 反序列化为 DataFrame

#### Scenario: 缓存自定义对象
- **WHEN** 缓存 StockInfo 等自定义对象
- **THEN** MUST 支持 pickle 序列化
- **AND** 读取时 MUST 反序列化为原类型对象
