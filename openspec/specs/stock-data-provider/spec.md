## ADDED Requirements

### Requirement: Provider 抽象接口
系统 MUST 定义一个抽象的 Provider 基类，所有数据提供者实现 MUST 继承该基类。Provider 基类 MUST 定义以下方法：
- `get_stock_info(stock_code: str) -> StockInfo`: 获取股票基本信息
- `get_history_data(stock_code: str, start_date: str, end_date: str, frequency: str) -> DataFrame`: 获取历史行情数据
- `get_dividend_data(stock_code: str) -> DataFrame`: 获取分红数据
- `get_financial_data(stock_code: str) -> DataFrame`: 获取财务数据

#### Scenario: 创建 Provider 实现
- **WHEN** 开发者创建新的数据提供者
- **THEN** MUST 继承自 BaseProvider 类
- **AND** MUST 实现所有定义的抽象方法

#### Scenario: 使用 Provider 获取数据
- **WHEN** 应用调用 Provider 的方法
- **THEN** MUST 返回标准化的数据格式
- **AND** 数据格式 MUST 符合 models 中定义的数据模型

### Requirement: baostock 数据源实现
系统 MUST 实现 baostock 数据提供者，支持以下功能：
- 连接 baostock 服务
- 查询股票基本信息（证券代码、证券名称、上市日期等）
- 查询历史行情数据（开盘价、收盘价、最高价、最低价、成交量等）
- 查询分红送股数据
- 查询财务数据（每股收益、净资产收益率等）
- 处理 baostock API 错误和异常

#### Scenario: 获取股票基本信息
- **WHEN** 调用 `get_stock_info("sh.600000")`
- **THEN** MUST 返回包含股票代码、名称、上市日期等信息的 StockInfo 对象
- **AND** 如果股票不存在，MUST 抛出 StockNotFoundError

#### Scenario: 获取历史行情数据
- **WHEN** 调用 `get_history_data("sh.600000", "2023-01-01", "2023-12-31", "d")`
- **THEN** MUST 返回包含日期、开盘价、收盘价等字段的 DataFrame
- **AND** 数据 MUST 按日期升序排列

#### Scenario: 处理 API 错误
- **WHEN** baostock API 返回错误
- **THEN** MUST 捕获异常并转换为自定义异常
- **AND** MUST 记录错误日志
- **AND** MUST 提供友好的错误信息

### Requirement: 批量数据查询
系统 MUST 支持批量查询接口，提高数据获取效率：
- `get_stocks_list(stock_type: str) -> DataFrame`: 获取股票列表
- `get_batch_history_data(stock_codes: List[str], start_date: str, end_date: str) -> Dict[str, DataFrame]`: 批量获取历史数据

#### Scenario: 批量获取历史数据
- **WHEN** 调用 `get_batch_history_data(["sh.600000", "sz.000001"], "2023-01-01", "2023-12-31")`
- **THEN** MUST 返回包含所有股票数据的字典
- **AND** MUST 遵守 API 频率限制（每秒不超过 1 次请求）

### Requirement: 速率限制
系统 MUST 实现速率限制器，控制对 baostock API 的调用频率：
- 默认每秒最多 1 次请求
- 支持自定义速率限制参数
- 请求超时 MUST 自动重试（最多 3 次）

#### Scenario: 速率限制生效
- **WHEN** 连续发起多个 API 请求
- **THEN** 请求间隔 MUST 不小于设定的速率限制（默认 1 秒）
- **AND** 超过速率限制的请求 MUST 等待直到可以发送

#### Scenario: 请求失败重试
- **WHEN** API 请求失败
- **THEN** 系统 MUST 自动重试
- **AND** 最多重试 3 次
- **AND** 重试间隔 MUST 递增（1s, 2s, 4s）

### Requirement: Provider 配置
系统 MUST 支持通过配置文件或环境变量配置 Provider 行为：
- API 请求超时时间
- 速率限制参数
- 重试次数和策略
- 是否启用调试日志

#### Scenario: 加载默认配置
- **WHEN** Provider 初始化时未提供配置
- **THEN** MUST 使用默认配置值
- **AND** 超时时间默认 30 秒
- **AND** 速率限制默认每秒 1 次请求

#### Scenario: 自定义配置
- **WHEN** Provider 初始化时提供自定义配置
- **THEN** MUST 使用自定义配置覆盖默认值
