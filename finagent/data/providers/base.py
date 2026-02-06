"""
数据提供者基类和异常定义
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

import pandas as pd

from finagent.data.models.stock import StockInfo, DividendInfo, FinancialInfo


class StockNotFoundError(Exception):
    """股票未找到异常"""

    pass


class DataProviderError(Exception):
    """数据提供者异常"""

    pass


class BaseProvider(ABC):
    """
    数据提供者抽象基类

    定义了所有数据提供者必须实现的接口。
    """

    @abstractmethod
    def get_stock_info(self, stock_code: str) -> StockInfo:
        """
        获取股票基本信息

        Args:
            stock_code: 股票代码 (如 "sh.600000")

        Returns:
            股票基本信息

        Raises:
            StockNotFoundError: 股票不存在
        """
        pass

    @abstractmethod
    def get_history_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
    ) -> pd.DataFrame:
        """
        获取历史行情数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 (d=日k, w=周, m=月)

        Returns:
            包含历史行情数据的 DataFrame

        Raises:
            StockNotFoundError: 股票不存在
        """
        pass

    @abstractmethod
    def get_dividend_data(self, stock_code: str) -> pd.DataFrame:
        """
        获取分红数据

        Args:
            stock_code: 股票代码

        Returns:
            包含分红数据的 DataFrame

        Raises:
            StockNotFoundError: 股票不存在
        """
        pass

    @abstractmethod
    def get_financial_data(
        self,
        stock_code: str,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        获取财务数据

        Args:
            stock_code: 股票代码
            year: 年份 (可选)
            quarter: 季度 (可选，1-4)

        Returns:
            包含财务数据的 DataFrame

        Raises:
            StockNotFoundError: 股票不存在
        """
        pass

    @abstractmethod
    def get_stocks_list(self, stock_type: str = "all") -> pd.DataFrame:
        """
        获取股票列表

        Args:
            stock_type: 股票类型 (all/sh/sz)

        Returns:
            包含股票列表的 DataFrame
        """
        pass
