"""
FinAgent 数据模型

定义股票相关的数据类。
"""

from finagent.data.models.stock import (
    StockInfo,
    StockHistory,
    DividendInfo,
    FinancialInfo,
)

__all__ = ["StockInfo", "StockHistory", "DividendInfo", "FinancialInfo"]
