## Why

目前的股权计算功能使用 mock 数据，无法支持真实的选股分析场景。需要构建一个可扩展的选股基础设施，集成 baostock 数据源，为未来的金融分析工具提供真实、可靠的数据支撑。

## What Changes

- **新增选股数据基础设施**：构建可扩展的数据获取层
- **集成 baostock 数据源**：实现与 baostock API 的对接
- **数据缓存机制**：减少重复请求，提高性能
- **数据模型标准化**：统一股票数据格式，便于上层应用使用

## Capabilities

### New Capabilities

- `stock-data-provider`: 股票数据提供者能力，封装数据获取逻辑，支持多种数据源（初期实现 baostock）
- `stock-data-cache`: 股票数据缓存能力，提供本地缓存机制，减少外部 API 调用
- `stock-selection-criteria`: 选股标准定义能力，支持可配置的选股条件

### Modified Capabilities

暂无现有能力需要修改。

## Impact

- **新增依赖**：baostock Python SDK
- **新增模块**：
  - `finagent/data/` - 数据层模块
  - `finagent/data/providers/` - 数据提供者
  - `finagent/data/cache/` - 缓存层
  - `finagent/data/models/` - 数据模型
- **现有影响**：`dividend-yield-calculator` skill 将从使用 mock 数据切换到真实数据源
