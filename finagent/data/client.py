"""
数据客户端

统一的数据访问入口，封装数据提供者和缓存逻辑。
"""

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from finagent.data.cache.sqlite import SQLiteCache
from finagent.data.models.stock import DividendInfo, FinancialInfo, StockInfo, StockHistory
from finagent.data.providers.baostock import BaoStockProvider


@dataclass
class DataClientConfig:
    """数据客户端配置"""

    # Provider 配置
    provider: str = "baostock"  # 数据提供者类型
    rate_limit: float = 1.0  # API 请求速率限制（秒）
    enable_cache: bool = True  # 是否启用缓存

    # 缓存配置
    cache_path: Optional[str] = None  # 缓存文件路径

    # 重试配置
    max_retries: int = 3  # 最大重试次数
    retry_delay: float = 1.0  # 重试延迟（秒）

    # 其他
    timeout: int = 30  # 请求超时时间（秒）


class DataClient:
    """
    数据客户端

    提供统一的数据访问接口，自动处理缓存和降级。
    """

    def __init__(self, config: Optional[DataClientConfig] = None):
        """
        初始化数据客户端

        Args:
            config: 客户端配置
        """
        self.config = config or DataClientConfig()

        # 初始化缓存
        self.cache = None
        if self.config.enable_cache:
            self.cache = SQLiteCache(db_path=self.config.cache_path)

        # 初始化数据提供者
        self.provider = self._create_provider()

    def _create_provider(self) -> BaoStockProvider:
        """创建数据提供者"""
        if self.config.provider == "baostock":
            return BaoStockProvider(
                cache=self.cache,
                rate_limit=self.config.rate_limit,
                enable_cache=self.config.enable_cache,
            )
        else:
            raise ValueError(f"不支持的数据提供者: {self.config.provider}")

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """
        获取股票基本信息

        Args:
            stock_code: 股票代码 (如 "sh.600000")

        Returns:
            股票基本信息
        """
        return self.provider.get_stock_info(stock_code)

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
        """
        return self.provider.get_history_data(stock_code, start_date, end_date, frequency)

    def get_dividend_data(self, stock_code: str) -> pd.DataFrame:
        """
        获取分红数据

        Args:
            stock_code: 股票代码

        Returns:
            包含分红数据的 DataFrame
        """
        return self.provider.get_dividend_data(stock_code)

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
        """
        return self.provider.get_financial_data(stock_code, year, quarter)

    def get_stocks_list(self, stock_type: str = "all") -> pd.DataFrame:
        """
        获取股票列表

        Args:
            stock_type: 股票类型 (all/sh/sz)

        Returns:
            包含股票列表的 DataFrame
        """
        return self.provider.get_stocks_list(stock_type)

    def get_batch_history_data(
        self,
        stock_codes: list[str],
        start_date: str,
        end_date: str,
        frequency: str = "d",
    ) -> dict[str, pd.DataFrame]:
        """
        批量获取历史数据

        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 (d=日k, w=周, m=月)

        Returns:
            股票代码到数据的映射字典
        """
        return self.provider.get_batch_history_data(stock_codes, start_date, end_date, frequency)

    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        if self.cache:
            return self.cache.get_stats()
        return {"hits": 0, "misses": 0, "total": 0, "hit_rate": 0, "cache_size": 0}

    def clear_cache(self) -> None:
        """清空缓存"""
        if self.cache:
            self.cache.clear()

    def cleanup_cache(self) -> int:
        """清理过期缓存"""
        if self.cache:
            return self.cache.cleanup_expired()
        return 0

    def close(self) -> None:
        """关闭客户端"""
        if self.cache:
            self.cache.close()
