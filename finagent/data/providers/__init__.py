"""
FinAgent 数据提供者

包含数据提供者基类和具体实现。
"""

from finagent.data.providers.base import BaseProvider, StockNotFoundError, DataProviderError
from finagent.data.providers.baostock import BaoStockProvider

__all__ = [
    "BaseProvider",
    "BaoStockProvider",
    "StockNotFoundError",
    "DataProviderError",
]
