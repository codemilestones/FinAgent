## ADDED Requirements

### Requirement: 选股条件定义
系统 MUST 支持定义可配置的选股条件，包括：
- 基本面条件：市盈率、市净率、股息率、净资产收益率等
- 技术面条件：价格区间、成交量、涨跌幅等
- 财务条件：营收增长率、净利润增长率等
- 自定义条件：支持用户自定义筛选逻辑

#### Scenario: 定义市盈率筛选条件
- **WHEN** 设置市盈率筛选条件为 0 < PE < 20
- **THEN** 系统 MUST 筛选出市盈率在 0 到 20 之间的股票

#### Scenario: 组合多个筛选条件
- **WHEN** 同时设置市盈率 < 20 且股息率 > 3%
- **THEN** 系统 MUST 返回同时满足两个条件的股票

### Requirement: 选股条件配置格式
系统 MUST 支持通过配置文件定义选股条件，配置格式 MUST 为 YAML 或 JSON：

#### Scenario: YAML 配置示例
```yaml
name: "高股息低估值策略"
conditions:
  - type: "pe_ratio"
    operator: "less_than"
    value: 20
  - type: "dividend_yield"
    operator: "greater_than"
    value: 0.03
  - type: "market_cap"
    operator: "greater_than"
    value: 10000000000
```

#### Scenario: JSON 配置示例
```json
{
  "name": "高股息低估值策略",
  "conditions": [
    {"type": "pe_ratio", "operator": "less_than", "value": 20},
    {"type": "dividend_yield", "operator": "greater_than", "value": 0.03}
  ]
}
```

### Requirement: 选股执行
系统 MUST 提供选股执行功能：
- 从数据源获取股票数据
- 根据配置的条件筛选股票
- 返回符合条件的股票列表
- 支持排序和分页

#### Scenario: 执行选股策略
- **WHEN** 调用 `execute_strategy(config)`
- **THEN** 系统 MUST 获取所有 A 股数据
- **AND** MUST 按配置条件筛选
- **AND** MUST 返回符合条件的股票列表

#### Scenario: 选股结果排序
- **WHEN** 配置中指定排序字段为 "dividend_yield" 且降序
- **THEN** 结果 MUST 按股息率从高到低排序

### Requirement: 条件运算符
系统 MUST 支持以下比较运算符：
- `equal`: 等于
- `not_equal`: 不等于
- `greater_than`: 大于
- `less_than`: 小于
- `greater_equal`: 大于等于
- `less_equal`: 小于等于
- `between`: 在区间内
- `contains`: 包含（用于字符串或多值字段）
- `in`: 在列表中

#### Scenario: 使用 between 运算符
- **WHEN** 设置条件为市盈率在 10 到 20 之间
- **THEN** MUST 使用 `between` 运算符
- **AND** MUST 返回 10 <= PE <= 20 的股票

#### Scenario: 使用 in 运算符
- **WHEN** 设置条件为行业在 ["银行", "保险"] 中
- **THEN** MUST 使用 `in` 运算符
- **AND** MUST 返回属于银行或保险行业的股票

### Requirement: 数据字段映射
系统 MUST 定义标准的数据字段名称，并支持与不同数据源的字段映射：

| 标准字段 | 描述 | baostock 字段 |
|---------|------|--------------|
| code | 股票代码 | code |
| name | 股票名称 | code_name |
| pe_ratio | 市盈率 | peTTM |
| pb_ratio | 市净率 | pbMRQ |
| dividend_yield | 股息率 | (计算) |
| market_cap | 市值 | (计算) |
| roe | 净资产收益率 | roeAvg |

#### Scenario: 字段自动映射
- **WHEN** 使用 baostock 数据源查询市盈率
- **THEN** 系统 MUST 自动将标准字段 `pe_ratio` 映射为 baostock 的 `peTTM`

### Requirement: 选股结果输出
系统 MUST 支持多种输出格式：
- pandas.DataFrame
- CSV 文件
- Excel 文件
- JSON 格式

#### Scenario: 输出为 DataFrame
- **WHEN** 调用 `execute_strategy(config, output="dataframe")`
- **THEN** MUST 返回 pandas.DataFrame

#### Scenario: 导出为 CSV
- **WHEN** 调用 `execute_strategy(config, output="csv", path="result.csv")`
- **THEN** MUST 将结果保存为 CSV 文件

### Requirement: 选股策略验证
系统 MUST 在执行选股前验证配置的有效性：
- 检查条件类型是否支持
- 检查运算符是否适用于该字段类型
- 检查值的范围是否合理

#### Scenario: 验证失败
- **WHEN** 配置中使用了不存在的条件类型
- **THEN** MUST 抛出 InvalidConditionError
- **AND** 错误信息 MUST 说明具体问题

### Requirement: 预设策略
系统 MUST 提供常用选股策略预设：
- 高股息策略
- 低估值策略
- 成长股策略
- 蓝筹股策略

#### Scenario: 使用预设策略
- **WHEN** 调用 `get_preset_strategy("high_dividend")`
- **THEN** MUST 返回高股息策略的配置
- **AND** 用户可以在此基础上修改
