---
name: dividend-yield-calculator
description: A股预期股息率计算工具。使用五步法计算单一股票或批量股票的预期股息率、派息率稳定性指标和业绩稳定性指标。当用户询问股票分红、股息率计算、派息率分析时使用此skill。
---

# A股预期股息率计算器

## 概述

本skill提供基于五步法的A股预期股息率计算工具，可以：

1. 计算单一股票的预期股息率
2. 批量计算多只股票的股息率
3. 分析派息率稳定性指标
4. 分析业绩稳定性指标
5. 根据行业、大股东需求、公告进行调整

## 核心概念

- **派息率**：公司每赚100元分给股东多少元（如30%表示盈利100元分红30元）
- **股息率**：投资100元每年收到多少分红（如5%表示投资100元每年分红5元）
- **预期股息率**：未来预期可获得的股息率，而非历史股息率

## 快速开始

### 使用Python脚本计算

```bash
# 计算单一股票
python scripts/dividend_calculator.py --stock-code 600036 --price 41.2

# 批量计算示例
python scripts/dividend_calculator.py --batch

# 输出JSON格式
python scripts/dividend_calculator.py --batch --json
```

### Python代码示例

```python
from scripts.dividend_calculator import (
    CompanyData, DividendRecord, CompanyType,
    AdjustmentFactors, calculate_dividend_yield
)

# 创建公司数据
company = CompanyData(
    stock_code="600036",
    stock_name="招商银行",
    company_type=CompanyType.A,
    current_price=41.2,
    dividend_records=[
        DividendRecord(year=2023, eps=5.66, dividend_per_share=1.92, payout_ratio=33.92),
        DividendRecord(year=2024, eps=5.6, dividend_per_share=1.90, payout_ratio=33.99),
    ]
)

# 计算股息率
result = calculate_dividend_yield(company)
print(f"预期股息率: {result['final_yield']:.2f}%")
```

## 公司分类

根据**业绩稳定性**和**派息率稳定性**将公司分为四类：

| 类型 | 业绩稳定性 | 派息率稳定性 | 代表行业 |
|------|-----------|-------------|----------|
| **A类** | 稳定 | 稳定 | 银行、公用事业、电信、铁路、茅台 |
| **B类** | 不稳定 | 稳定 | 海运、白酒、煤、有色、化工 |
| **C类** | 稳定 | 不稳定 | 火电、水务、燃气、家电、高铁 |
| **D类** | 不稳定 | 不稳定 | 不推荐新手投资 |

## 五步计算法

### 1. 测算基准预期股息率

```
基准股息率 = 预期EPS × 平均派息率 ÷ 当前股价
```

取最近两年数据计算平均派息率。

### 2. 行业基准纠正

- **A类**：一般不需纠正，除非有考核目标或管理层表态
- **B类**：根据周期调整（顶部下调，底部上调）
- **C类**：根据资本开支调整（大额投资下调，出售资产上调）

### 3. 大股东需求纠正

大股东急需用钱时可能加大派息率。

### 4. 公告纠正

优先考虑公司公告的分红承诺（确定性最高）。

## 稳定性指标

### 派息率稳定性

| 标准差 | 等级 |
|-------|------|
| < 5% | 稳定 |
| 5-10% | 较稳定 |
| > 10% | 不稳定 |

### 业绩稳定性

| EPS变化率标准差 | 等级 |
|---------------|------|
| < 10% | 稳定 |
| 10-20% | 较稳定 |
| > 20% | 不稳定 |

## 使用场景

1. **单一股票分析**：分析某只A股的预期股息率
2. **批量筛选**：批量计算多只股票找出高股息率标的
3. **稳定性评估**：评估公司分红的稳定性和可预测性
4. **投资决策**：辅助判断是否值得投资

## 参考资料

详细的计算方法论请参考：[references/dividend_methodology.md](references/dividend_methodology.md)
