# FinAgent 配置说明

本文档详细说明 FinAgent 数据基础设施的配置选项。

## DataClientConfig 配置

### 完整配置示例

```python
from finagent.data.client import DataClient, DataClientConfig

config = DataClientConfig(
    # Provider 配置
    provider="baostock",       # 数据提供者类型
    rate_limit=1.0,            # API 请求速率限制（秒）

    # 缓存配置
    enable_cache=True,         # 是否启用缓存
    cache_path=None,           # 缓存文件路径（None 表示使用默认路径）

    # 重试配置
    max_retries=3,             # 最大重试次数
    retry_delay=1.0,           # 重试延迟（秒）

    # 其他
    timeout=30,                # 请求超时时间（秒）
)

client = DataClient(config)
```

### 配置参数详解

#### Provider 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider` | str | `"baostock"` | 数据提供者类型，当前仅支持 `"baostock"` |
| `rate_limit` | float | `1.0` | API 请求速率限制，单位：秒/次。设置为 1.0 表示每秒最多 1 次请求 |

**速率限制说明**：
- baostock 建议每秒不超过 1 次请求
- 设置过高的速率可能导致 IP 被封禁
- 对于个人使用，建议保持默认值 `1.0`

#### 缓存配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_cache` | bool | `True` | 是否启用缓存。禁用缓存会导致每次查询都调用 API |
| `cache_path` | str | `None` | 缓存文件路径。`None` 表示使用默认路径 `~/.finagent/cache.db` |

**缓存路径说明**：
- 默认路径：`~/.finagent/cache.db`（用户主目录下的 `.finagent` 文件夹）
- 可以指定自定义路径，如：`"/tmp/finagent_cache.db"`
- 确保指定的目录存在且有写入权限

#### 重试配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_retries` | int | `3` | 请求失败时的最大重试次数 |
| `retry_delay` | float | `1.0` | 重试之间的延迟时间，单位：秒 |

**重试机制说明**：
- 当 API 请求失败时，会自动重试
- 重试次数达到上限后抛出异常
- 网络不稳定时可适当增加 `max_retries`

#### 超时配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | int | `30` | 单次请求的超时时间，单位：秒 |

## 缓存 TTL 配置

### 默认 TTL 策略

不同数据类型使用不同的缓存有效期（TTL）：

| 数据类型 | TTL | 说明 |
|----------|-----|------|
| `stock_info` | 30 天 (2,592,000 秒) | 股票基本信息变化较少 |
| `history` | 7 天 (604,800 秒) | 历史行情数据 |
| `dividend` | 1 天 (86,400 秒) | 分红数据 |
| `financial` | 1 天 (86,400 秒) | 财务数据 |

### 自定义 TTL

如需自定义 TTL，可以在调用缓存方法时指定：

```python
# 设置缓存时指定 TTL（秒）
client.cache.set("custom_key", data, ttl=3600)  # 1 小时
```

## 缓存管理

### 查看缓存统计

```python
stats = client.get_cache_stats()

print(f"命中次数: {stats['hits']}")
print(f"未命中次数: {stats['misses']}")
print(f"命中率: {stats['hit_rate'] * 100:.1f}%")
print(f"缓存大小: {stats['cache_size']} 条")
```

### 清空缓存

```python
# 清空所有缓存
client.clear_cache()

print("缓存已清空")
```

### 清理过期缓存

```python
# 清理过期的缓存条目
removed_count = client.cleanup_cache()

print(f"已清理 {removed_count} 条过期缓存")
```

## 环境变量配置

当前版本不支持通过环境变量配置。所有配置通过 `DataClientConfig` 传递。

## 配置场景示例

### 开发环境

```python
config = DataClientConfig(
    provider="baostock",
    rate_limit=1.0,
    enable_cache=True,
    max_retries=3,
)
```

### 生产环境

```python
config = DataClientConfig(
    provider="baostock",
    rate_limit=1.0,
    enable_cache=True,
    cache_path="/var/cache/finagent/cache.db",
    max_retries=5,
    retry_delay=2.0,
    timeout=60,
)
```

### 测试环境（禁用缓存）

```python
config = DataClientConfig(
    provider="baostock",
    rate_limit=1.0,
    enable_cache=False,  # 禁用缓存
    max_retries=1,
)
```

### 高频率查询

```python
config = DataClientConfig(
    provider="baostock",
    rate_limit=0.5,  # 每 2 秒 1 次请求，更保守
    enable_cache=True,
    max_retries=5,
)
```

## 常见问题

### Q: 如何选择 rate_limit？

A: 根据数据源的限制和您的需求：
- baostock 建议不超过 1 次/秒
- 批量查询时可适当降低速率
- 个人使用建议保持默认值 1.0

### Q: 缓存文件可以删除吗？

A: 可以。删除缓存文件后，下次查询会重新从 API 获取数据并重建缓存。

### Q: 如何更改缓存位置？

A: 使用 `cache_path` 参数：
```python
config = DataClientConfig(
    cache_path="/path/to/custom/cache.db",
)
```

### Q: 缓存会占用多少空间？

A: 取决于查询的数据量。一般来说：
- 单只股票的历史数据（一年）：约 10-50 KB
- 100 只股票的基本信息：约 5-10 MB
- 如果空间不足，可以定期清理缓存

## 性能优化建议

1. **启用缓存**：缓存可以显著提高性能，减少 API 调用
2. **批量查询**：使用 `get_batch_history_data` 批量获取数据
3. **合理设置 TTL**：根据数据变化频率设置合理的缓存时间
4. **定期清理**：定期清理过期缓存，避免数据库过大
