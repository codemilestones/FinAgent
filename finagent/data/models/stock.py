"""
股票数据模型

定义股票相关的数据类。
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class StockInfo:
    """股票基本信息"""

    code: str  # 股票代码 (如 "sh.600000")
    name: str  # 股票名称
    ipo_date: Optional[date]  # 上市日期
    industry: Optional[str] = None  # 行业
    market: Optional[str] = None  # 市场 (上海/深圳)
    type: Optional[str] = None  # 类型 (股票/指数等)

    def __str__(self) -> str:
        return f"{self.code} {self.name}"


@dataclass
class StockHistory:
    """股票历史行情数据"""

    code: str  # 股票代码
    date: date  # 交易日期
    open: Optional[float]  # 开盘价
    high: Optional[float]  # 最高价
    low: Optional[float]  # 最低价
    close: Optional[float]  # 收盘价
    volume: Optional[float]  # 成交量
    amount: Optional[float]  # 成交额

    # 复权因子
    adj_factor: Optional[float] = None

    def __str__(self) -> str:
        return f"{self.code} {self.date} 收盘:{self.close}"


@dataclass
class DividendInfo:
    """股票分红信息"""

    code: str  # 股票代码
    dividend_year: Optional[int] = None  # 分红年度
    dividend_ratio: Optional[float] = None  # 每股分红
    transfer_ratio: Optional[float] = None  # 每股转增
    record_date: Optional[date] = None  # 股权登记日
    ex_date: Optional[date] = None  # 除权除息日
    pay_date: Optional[date] = None  # 派息日

    def __str__(self) -> str:
        return f"{self.code} {self.dividend_year} 分红:{self.dividend_ratio}"


@dataclass
class FinancialInfo:
    """股票财务信息"""

    code: str  # 股票代码
    report_date: Optional[date] = None  # 报告期
    report_type: Optional[str] = None  # 报告类型 (年报/季报等)

    # 盈利能力
    eps: Optional[float] = None  # 每股收益
    roe: Optional[float] = None  # 净资产收益率
    roa: Optional[float] = None  # 总资产收益率
    gross_profit_margin: Optional[float] = None  # 毛利率
    net_profit_margin: Optional[float] = None  # 净利率

    # 估值指标
    pe_ratio: Optional[float] = None  # 市盈率
    pb_ratio: Optional[float] = None  # 市净率
    ps_ratio: Optional[float] = None  # 市销率

    # 偿债能力
    current_ratio: Optional[float] = None  # 流动比率
    quick_ratio: Optional[float] = None  # 速动比率
    debt_to_asset: Optional[float] = None  # 资产负债率

    # 营运能力
    inventory_turnover: Optional[float] = None  # 存货周转率
    receivable_turnover: Optional[float] = None  # 应收账款周转率

    # 成长能力
    revenue_growth: Optional[float] = None  # 营收增长率
    profit_growth: Optional[float] = None  # 利润增长率

    def __str__(self) -> str:
        return f"{self.code} {self.report_date} PE:{self.pe_ratio} PB:{self.pb_ratio}"
