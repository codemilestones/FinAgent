# FinAgent 选股基础设施

FinAgent 的选股基础设施，提供可扩展的股票数据获取、缓存和选股条件筛选能力。

## 功能特性

- **多数据源支持**: 通过 Provider 抽象层支持多个数据源
- **智能缓存**: 基于 SQLite 的本地缓存，减少 API 调用
- **速率限制**: 内置速率限制器，避免触发 API 频率限制
- **选股条件**: 可配置的选股条件和预设策略
- **数据模型**: 标准化的股票数据模型

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 使用数据客户端

```python
from finagent.data import DataClient, DataClientConfig

# 创建数据客户端
config = DataClientConfig(
    provider="baostock",
    enable_cache=True,
    rate_limit=1.0,
)
client = DataClient(config)

# 获取股票信息
stock_info = client.get_stock_info("sh.600000")
print(f"{stock_info.code} {stock_info.name}")

# 获取历史行情数据
history_df = client.get_history_data(
    stock_code="sh.600000",
    start_date="2023-01-01",
    end_date="2023-12-31",
)
print(history_df.head())

# 关闭客户端
client.close()
```

### 2. 使用选股策略

```python
from finagent.data import DataClient
from finagent.data.criteria import Strategy, StrategyExecutor, Condition, Operator

# 创建数据客户端
client = DataClient()

# 创建选股策略
strategy = Strategy(
    name="高股息低估值",
    description="筛选高股息且低估值股票",
    conditions=[
        Condition(type="dividend_yield", operator=Operator.GREATER_THAN, value=0.03),
        Condition(type="pe_ratio", operator=Operator.LESS_THAN, value=20),
    ],
    sort_by="dividend_yield",
    sort_order="desc",
)

# 执行策略
executor = StrategyExecutor(client)
result_df = executor.execute(strategy)
print(result_df)

client.close()
```

### 3. 使用预设策略

```python
from finagent.data import DataClient
from finagent.data.criteria import StrategyExecutor

client = DataClient()
executor = StrategyExecutor(client)

# 获取预设策略
strategy = StrategyExecutor.get_preset_strategy("high_dividend")
result_df = executor.execute(strategy)
print(result_df)

# 列出所有预设策略
print(StrategyExecutor.list_preset_strategies())
# ['high_dividend', 'low_valuation', 'blue_chip']
```

## 架构设计

```
finagent/
├── data/
│   ├── models/          # 数据模型
│   │   └── stock.py      # StockInfo, StockHistory, DividendInfo, FinancialInfo
│   ├── providers/       # 数据提供者
│   │   ├── base.py       # BaseProvider 抽象类
│   │   └── baostock.py   # BaoStock 数据源实现
│   ├── cache/           # 缓存层
│   │   └── sqlite.py     # SQLite 缓存实现
│   ├── criteria/        # 选股条件
│   │   └── condition.py  # Condition, Strategy, StrategyExecutor
│   └── client.py        # 数据客户端入口
└── utils/
    └── rate_limiter.py   # 速率限制器
```

## 数据模型

### StockInfo
股票基本信息：
- `code`: 股票代码 (如 "sh.600000")
- `name`: 股票名称
- `ipo_date`: 上市日期
- `industry`: 行业
- `market`: 市场

### FinancialInfo
财务指标信息：
- `pe_ratio`: 市盈率
- `pb_ratio`: 市净率
- `roe`: 净资产收益率
- `eps`: 每股收益
- 等等

## 配置选项

### DataClientConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| provider | str | "baostock" | 数据提供者类型 |
| rate_limit | float | 1.0 | API 请求速率限制（秒） |
| enable_cache | bool | True | 是否启用缓存 |
| cache_path | str | None | 缓存文件路径 |

## 缓存策略

不同数据类型使用不同的默认 TTL：

| 数据类型 | TTL |
|----------|-----|
| 股票基本信息 | 30 天 |
| 历史行情数据 | 7 天 |
| 分红数据 | 1 天 |
| 财务数据 | 1 天 |

## 预设策略

| 策略名称 | 说明 | 条件 |
|----------|------|------|
| high_dividend | 高股息策略 | 股息率 > 3%, PE < 30 |
| low_valuation | 低估值策略 | PE < 15, PB < 2 |
| blue_chip | 蓝筹股策略 | 市值 > 1000亿, PE 10-30, ROE > 10% |

## 开发

### 运行示例

```bash
# 查看帮助
python -m finagent.data.examples.real_data_dividend_calculator --help

# 计算单只股票股息率
python -m finagent.data.examples.real_data_dividend_calculator \
    --stock-code sh.600036 \
    --price 41.2 \
    --use-real-data
```

### 代码格式化

```bash
# 格式化代码
black finagent/
isort finagent/

# 代码检查
flake8 finagent/
pylint finagent/
```

## 许可证

MIT License
