## 1. 项目设置

- [x] 1.1 创建 `finagent/` Python 包目录结构
- [x] 1.2 添加 `baostock` 依赖到 `pyproject.toml` 或 `requirements.txt`
- [x] 1.3 添加 `pandas` 依赖（如果尚未添加）
- [x] 1.4 创建 `__init__.py` 文件使目录成为 Python 包

## 2. 数据模型层 (models)

- [x] 2.1 创建 `finagent/data/models/__init__.py`
- [x] 2.2 定义 `StockInfo` 数据类（包含股票代码、名称、上市日期等）
- [x] 2.3 定义 `StockHistory` 数据类（包含日期、开盘价、收盘价等）
- [x] 2.4 定义 `DividendInfo` 数据类（包含分红信息）
- [x] 2.5 定义 `FinancialInfo` 数据类（包含财务指标）

## 3. 工具层 (utils)

- [x] 3.1 创建 `finagent/utils/__init__.py`
- [x] 3.2 实现 `RateLimiter` 类（支持请求速率控制）
- [x] 3.3 实现 `RetryDecorator` 装饰器（支持自动重试）
- [ ] 3.4 编写速率限制器单元测试

## 4. 缓存层 (cache)

- [x] 4.1 创建 `finagent/data/cache/__init__.py`
- [x] 4.2 定义 `BaseCache` 抽象类
- [x] 4.3 实现 `SQLiteCache` 类（继承 BaseCache）
- [x] 4.4 实现缓存数据库初始化逻辑
- [x] 4.5 实现缓存 TTL 自动过期机制
- [x] 4.6 实现缓存键生成工具（`generate_cache_key`）
- [x] 4.7 实现缓存统计功能（命中次数、命中率等）
- [x] 4.8 实现缓存管理功能（清空、刷新、清理过期）
- [x] 4.9 实现数据序列化/反序列化（DataFrame、自定义对象）
- [ ] 4.10 编写缓存层单元测试

## 5. 数据提供者层 (providers)

- [x] 5.1 创建 `finagent/data/providers/__init__.py`
- [x] 5.2 定义 `BaseProvider` 抽象类
- [x] 5.3 定义抽象方法：`get_stock_info`、`get_history_data`、`get_dividend_data`、`get_financial_data`
- [x] 5.4 定义自定义异常类：`StockNotFoundError`、`DataProviderError`
- [x] 5.5 实现 `BaoStockProvider` 类（继承 BaseProvider）
- [x] 5.6 实现 baostock 连接和登录逻辑
- [x] 5.7 实现 `get_stock_info` 方法
- [x] 5.8 实现 `get_history_data` 方法
- [x] 5.9 实现 `get_dividend_data` 方法
- [x] 5.10 实现 `get_financial_data` 方法
- [x] 5.11 实现 `get_stocks_list` 方法（获取股票列表）
- [x] 5.12 实现 `get_batch_history_data` 方法（批量查询）
- [x] 5.13 集成 `RateLimiter` 控制请求频率
- [x] 5.14 集成 `SQLiteCache` 实现数据缓存
- [x] 5.15 实现错误处理和降级逻辑
- [x] 5.16 实现字段映射（标准字段 <-> baostock 字段）
- [ ] 5.17 编写 baostock provider 单元测试

## 6. 数据客户端 (client)

- [x] 6.1 创建 `finagent/data/client.py`
- [x] 6.2 实现 `DataClient` 类（统一数据访问入口）
- [x] 6.3 实现自动选择 provider 的逻辑
- [x] 6.4 实现缓存优先的数据获取策略
- [x] 6.5 添加配置支持（超时、速率限制、重试等）
- [ ] 6.6 编写客户端集成测试

## 7. 选股条件层 (criteria)

- [x] 7.1 创建 `finagent/data/criteria/` 目录
- [x] 7.2 定义 `Condition` 数据类
- [x] 7.3 定义 `Strategy` 配置类
- [x] 7.4 实现条件运算符解析（equal、greater_than、between 等）
- [x] 7.5 实现条件验证逻辑
- [x] 7.6 实现 `StrategyExecutor` 类
- [x] 7.7 实现数据筛选逻辑
- [x] 7.8 实现结果排序和分页
- [x] 7.9 实现输出格式转换（DataFrame、CSV、JSON）
- [x] 7.10 实现预设策略（高股息、低估值等）
- [ ] 7.11 编写选股条件单元测试

## 8. 集成到 dividend-yield-calculator

- [x] 8.1 修改 dividend-yield-calculator skill 使用新数据源
- [x] 8.2 添加配置选项（真实数据 vs mock 数据）
- [x] 8.3 更新 skill 脚本适配新的数据格式
- [x] 8.4 保持向后兼容性
- [ ] 8.5 更新 skill 文档

## 9. 测试和文档

- [ ] 9.1 编写端到端集成测试
- [ ] 9.2 编写使用示例代码
- [ ] 9.3 编写 README 文档
- [ ] 9.4 编写 API 文档
- [ ] 9.5 添加配置说明文档
- [ ] 9.6 性能测试和优化

## 10. 项目清理

- [ ] 10.1 运行所有测试确保通过
- [ ] 10.2 代码格式化（black、isort）
- [ ] 10.3 代码检查（flake8、pylint）
- [ ] 10.4 更新项目主 README
- [ ] 10.5 提交代码到 git
