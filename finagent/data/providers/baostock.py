"""
BaoStock 数据提供者实现

使用 baostock API 获取股票数据。
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import baostock as bs
import pandas as pd

from finagent.data.cache.sqlite import SQLiteCache, generate_cache_key
from finagent.data.models.stock import StockInfo
from finagent.data.providers.base import BaseProvider, StockNotFoundError, DataProviderError
from finagent.utils.rate_limiter import RateLimiter, retry_on_exception

logger = logging.getLogger(__name__)

# 字段映射：标准字段 -> baostock 字段
FIELD_MAPPING = {
    # 历史行情字段
    "date": "date",
    "code": "code",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "amount": "amount",
    "adj_factor": "adjustflag",
    # 财务指标字段
    "pe_ratio": "peTTM",
    "pb_ratio": "pbMRQ",
    "ps_ratio": "psTTM",
    "pcf_ratio": "pcfNcfTTM",
    "roe": "roeAvg",
    "eps": "epsTTM",
}


class BaoStockProvider(BaseProvider):
    """
    BaoStock 数据提供者

    从 baostock 获取股票数据，支持缓存和速率限制。
    """

    def __init__(
        self,
        cache: Optional[SQLiteCache] = None,
        rate_limit: float = 1.0,
        enable_cache: bool = True,
    ):
        """
        初始化 BaoStockProvider

        Args:
            cache: 缓存实例，默认创建新实例
            rate_limit: API 请求速率限制（秒）
            enable_cache: 是否启用缓存
        """
        self.cache = cache if enable_cache else None
        if enable_cache and self.cache is None:
            self.cache = SQLiteCache()

        self.rate_limiter = RateLimiter(rate=rate_limit)
        self._lg = bs.login()
        if self._lg.error_code != "0":
            raise DataProviderError(f"BaoStock 登录失败: {self._lg.error_msg}")

    def __del__(self):
        """登出 BaoStock"""
        if hasattr(self, "_lg"):
            bs.logout()

    @retry_on_exception(max_retries=3, exceptions=(Exception,))
    def _query_with_rate_limit(
        self,
        rs: Any,
    ) -> pd.DataFrame:
        """
        使用速率限制执行查询

        Args:
            rs: BaoStock 查询结果

        Returns:
            查询结果 DataFrame
        """
        self.rate_limiter.acquire()

        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        return pd.DataFrame(data_list, columns=rs.fields)

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """获取股票基本信息"""
        cache_key = generate_cache_key("info", stock_code)

        # 检查缓存
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # 从 baostock 获取 - 先获取所有股票再筛选
        rs = bs.query_stock_basic()
        all_stocks = self._query_with_rate_limit(rs)

        # 筛选指定股票
        df = all_stocks[all_stocks["code"] == stock_code]

        if df.empty:
            raise StockNotFoundError(f"股票不存在: {stock_code}")

        row = df.iloc[0]
        info = StockInfo(
            code=row["code"],
            name=row["code_name"],
            ipo_date=self._parse_date(row["ipoDate"]),
            industry=None,  # baostock 基本信息不包含行业
        )

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, info, ttl=self.cache.DEFAULT_TTL["stock_info"])

        return info

    def get_history_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
    ) -> pd.DataFrame:
        """获取历史行情数据"""
        cache_key = generate_cache_key(
            "history",
            stock_code,
            start=start_date,
            end=end_date,
            freq=frequency,
        )

        # 检查缓存
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # 从 baostock 获取
        # 频率映射: d=日k, w=周, m=月
        freq_map = {"d": "d", "w": "w", "m": "m"}
        freq = freq_map.get(frequency, "d")

        rs = bs.query_history_k_data_plus(
            stock_code,
            "date,code,open,high,low,close,volume,amount,adjustflag",
            start_date=start_date,
            end_date=end_date,
            frequency=freq,
            adjustflag="2",  # 后复权
        )
        df = self._query_with_rate_limit(rs)

        if df.empty:
            logger.warning(f"未获取到历史数据: {stock_code} {start_date} - {end_date}")
            return pd.DataFrame()

        # 转换数据类型
        numeric_columns = ["open", "high", "low", "close", "volume", "amount"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache.DEFAULT_TTL["history"])

        return df

    def get_dividend_data(self, stock_code: str) -> pd.DataFrame:
        """获取分红数据"""
        cache_key = generate_cache_key("dividend", stock_code)

        # 检查缓存
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # 从 baostock 获取
        # 如果没有指定年份，获取近几年的分红数据
        years = ["2023", "2022", "2021", "2020"]

        all_dividends = []
        for year in years:
            rs = bs.query_dividend_data(
                code=stock_code,
                year=year,
                yearType="report",
            )
            df_year = self._query_with_rate_limit(rs)
            if not df_year.empty:
                all_dividends.append(df_year)

        if all_dividends:
            df = pd.concat(all_dividends, ignore_index=True)
        else:
            df = pd.DataFrame()

        if df.empty:
            logger.warning(f"未获取到分红数据: {stock_code}")
            return pd.DataFrame()

        # 转换数据类型
        numeric_columns = ["dividCashPsBeforeTax", "dividCashPsAfterTax", "dividStocksPs"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache.DEFAULT_TTL["dividend"])

        return df

    def get_financial_data(
        self,
        stock_code: str,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
    ) -> pd.DataFrame:
        """获取财务数据"""
        cache_key = generate_cache_key(
            "financial",
            stock_code,
            year=year or "",
            quarter=quarter or "",
        )

        # 检查缓存
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # 从 baostock 获取
        # 如果没有指定年份，默认获取最近4个季度的数据
        if not year:
            year = 2023  # 默认年份
        if not quarter:
            quarter = 4  # 默认季度

        year_str = str(year)
        quarter_str = str(quarter)

        rs = bs.query_profit_data(
            code=stock_code,
            year=year_str,
            quarter=quarter_str,
        )
        df = self._query_with_rate_limit(rs)

        if df.empty:
            logger.warning(f"未获取到财务数据: {stock_code}")
            return pd.DataFrame()

        # 转换数据类型
        numeric_columns = [
            "roeAvg",
            "npMargin",
            "gpMargin",
            "netProfit",
            "epsTTM",
            "MBRevenue",
            "totalProfit",
            "totalOperateRevenue",
            "totalOperateCost",
            "operateProfit",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 缓存结果
        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache.DEFAULT_TTL["financial"])

        return df

    def get_stocks_list(self, stock_type: str = "all") -> pd.DataFrame:
        """获取股票列表"""
        cache_key = f"stocks:list:{stock_type}"

        # 检查缓存
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # 从 baostock 获取
        rs = bs.query_stock_basic()
        df = self._query_with_rate_limit(rs)

        if df.empty:
            logger.warning("未获取到股票列表")
            return pd.DataFrame()

        # 缓存结果（股票列表变化较少，使用较长 TTL）
        if self.cache:
            self.cache.set(cache_key, df, ttl=7 * 24 * 3600)

        return df

    def get_batch_history_data(
        self,
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        frequency: str = "d",
    ) -> Dict[str, pd.DataFrame]:
        """批量获取历史数据"""
        results = {}
        for code in stock_codes:
            try:
                df = self.get_history_data(code, start_date, end_date, frequency)
                if not df.empty:
                    results[code] = df
            except Exception as e:
                logger.error(f"获取 {code} 历史数据失败: {e}")

        return results

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str or date_str == "":
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
