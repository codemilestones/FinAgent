# FinAgent

金融智能助手，提供金融计算和分析工具。

## 简介

FinAgent 是一个基于 Python 的金融分析工具集，通过 Claude Code 的 skill 机制提供各种金融计算和分析能力。

## 功能模块

### 1. 选股基础设施 (`finagent/`)

提供可扩展的股票数据获取、缓存和选股能力：

- **数据提供者**: 支持 baostock 等数据源，可扩展其他数据源
- **智能缓存**: 基于 SQLite 的本地缓存，减少 API 调用
- **速率限制**: 内置速率限制器，避免触发 API 频率限制
- **选股条件**: 可配置的选股条件和预设策略

```python
from finagent.data import DataClient, DataClientConfig

# 创建数据客户端
config = DataClientConfig(
    provider="baostock",
    enable_cache=True,
)
client = DataClient(config)

# 获取股票信息
stock_info = client.get_stock_info("sh.600000")
print(f"{stock_info.code} {stock_info.name}")

client.close()
```

详见 [finagent/README.md](finagent/README.md)

### 2. A股预期股息率计算器 (`dividend-yield-calculator`)

使用五步法计算股票的预期股息率：

1. 分类讨论（A/B/C/D类）
2. 测算基准
3. 行业基准纠正
4. 大股东需求纠正
5. 公告纠正

使用方式：
```
/dividend-yield-calculator
```

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 项目结构

```
FinAgent/
├── finagent/               # 选股基础设施
│   ├── data/
│   │   ├── models/         # 数据模型
│   │   ├── providers/      # 数据提供者
│   │   ├── cache/          # 缓存层
│   │   ├── criteria/       # 选股条件
│   │   └── client.py       # 数据客户端
│   └── utils/              # 工具类
│
├── .claude/
│   └── skills/             # Skills 目录
│       └── dividend-yield-calculator/
│
├── openspec/               # OpenSpec 工作流
│   └── changes/            # 变更记录
│
├── requirements.txt        # Python 依赖
└── README.md
```

## 开发指南

### 运行示例

```bash
# 获取股票数据示例
python -m finagent.data.examples.fetch_recent_data --stock-code sh.600036

# 计算股息率（真实数据）
python -m finagent.data.examples.real_data_dividend_calculator \
    --stock-code sh.600036 --price 41.2 --use-real-data

# 综合示例集合
python -m finagent.data.examples.comprehensive_examples

# 性能测试
python -m finagent.data.examples.performance_test
```

### 创建新 Skill

本项目使用 `skill-creator` 来创建新的 skill。详见 [CLAUDE.md](CLAUDE.md)。

### 使用 OpenSpec 工作流

项目支持 OpenSpec 实验性工作流：

- `/opsx:new` - 创建新变更
- `/opsx:ff` - 快速生成所有工件
- `/opsx:apply` - 实施变更
- `/opsx:verify` - 验证实施
- `/opsx:archive` - 归档已完成变更

### 代码格式化

```bash
# 格式化代码
black finagent/
isort finagent/

# 代码检查
flake8 finagent/
pylint finagent/
```

## 文档

- [finagent/README.md](finagent/README.md) - 选股基础设施文档
- [finagent/CONFIG.md](finagent/CONFIG.md) - 配置说明文档
- [.claude/skills/dividend-yield-calculator/SKILL.md](.claude/skills/dividend-yield-calculator/SKILL.md) - 股息率计算器文档

## 许可证

MIT License
