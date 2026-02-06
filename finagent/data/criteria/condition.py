"""
选股条件和策略执行器

支持可配置的选股条件和策略执行。
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class Operator(str, Enum):
    """条件运算符"""

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    BETWEEN = "between"
    CONTAINS = "contains"
    IN = "in"


class Condition(BaseModel):
    """选股条件"""

    type: str = Field(..., description="条件类型，如 pe_ratio, dividend_yield")
    operator: Operator = Field(..., description="运算符")
    value: Any = Field(..., description="条件值")

    @field_validator("value")
    def validate_value(cls, v, info):
        """验证条件值"""
        # between 运算符需要两个值的列表
        operator = info.data.get("operator")
        if operator == Operator.BETWEEN:
            if not isinstance(v, (list, tuple)) or len(v) != 2:
                raise ValueError("between 运算符需要两个值的列表")
        # in 运算符需要列表
        elif operator == Operator.IN:
            if not isinstance(v, (list, tuple)):
                raise ValueError("in 运算符需要列表值")
        return v

    def applies_to(self, row: pd.Series) -> bool:
        """
        检查条件是否应用于某行数据

        Args:
            row: 数据行

        Returns:
            是否满足条件
        """
        # 获取字段值
        field_value = row.get(self.type)

        # 处理 None 值
        if field_value is None:
            return False

        # 根据运算符判断
        if self.operator == Operator.EQUAL:
            return field_value == self.value
        elif self.operator == Operator.NOT_EQUAL:
            return field_value != self.value
        elif self.operator == Operator.GREATER_THAN:
            return float(field_value) > float(self.value)
        elif self.operator == Operator.LESS_THAN:
            return float(field_value) < float(self.value)
        elif self.operator == Operator.GREATER_EQUAL:
            return float(field_value) >= float(self.value)
        elif self.operator == Operator.LESS_EQUAL:
            return float(field_value) <= float(self.value)
        elif self.operator == Operator.BETWEEN:
            min_val, max_val = self.value
            return min_val <= float(field_value) <= max_val
        elif self.operator == Operator.CONTAINS:
            return str(self.value) in str(field_value)
        elif self.operator == Operator.IN:
            return field_value in self.value
        else:
            return False


@dataclass
class Strategy:
    """选股策略配置"""

    name: str  # 策略名称
    description: str = ""  # 策略描述
    conditions: List[Condition] = field(default_factory=list)  # 选股条件
    sort_by: Optional[str] = None  # 排序字段
    sort_order: str = "desc"  # 排序方向 (asc/desc)
    limit: Optional[int] = None  # 返回结果数量限制

    @classmethod
    def from_yaml(cls, file_path: str) -> "Strategy":
        """从 YAML 文件加载策略"""
        import yaml

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        conditions = [Condition(**c) for c in data.pop("conditions", [])]
        return cls(**data, conditions=conditions)

    @classmethod
    def from_json(cls, file_path: str) -> "Strategy":
        """从 JSON 文件加载策略"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conditions = [Condition(**c) for c in data.pop("conditions", [])]
        return cls(**data, conditions=conditions)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "conditions": [c.model_dump() for c in self.conditions],
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "limit": self.limit,
        }


class StrategyExecutor:
    """选股策略执行器"""

    # 预设策略
    PRESET_STRATEGIES = {
        "high_dividend": Strategy(
            name="高股息策略",
            description="筛选股息率较高的股票",
            conditions=[
                Condition(type="dividend_yield", operator=Operator.GREATER_THAN, value=0.03),
                Condition(type="pe_ratio", operator=Operator.LESS_THAN, value=30),
            ],
            sort_by="dividend_yield",
            sort_order="desc",
        ),
        "low_valuation": Strategy(
            name="低估值策略",
            description="筛选估值较低的股票",
            conditions=[
                Condition(type="pe_ratio", operator=Operator.LESS_THAN, value=15),
                Condition(type="pb_ratio", operator=Operator.LESS_THAN, value=2),
            ],
            sort_by="pe_ratio",
            sort_order="asc",
        ),
        "blue_chip": Strategy(
            name="蓝筹股策略",
            description="筛选市值大、业绩稳定的蓝筹股",
            conditions=[
                Condition(type="market_cap", operator=Operator.GREATER_THAN, value=100000000000),
                Condition(type="pe_ratio", operator=Operator.BETWEEN, value=[10, 30]),
                Condition(type="roe", operator=Operator.GREATER_THAN, value=0.1),
            ],
            sort_by="market_cap",
            sort_order="desc",
        ),
    }

    def __init__(self, data_client):
        """
        初始化策略执行器

        Args:
            data_client: 数据客户端实例
        """
        self.data_client = data_client

    def execute(
        self,
        strategy: Strategy,
        output_format: str = "dataframe",
    ) -> pd.DataFrame | dict | str:
        """
        执行选股策略

        Args:
            strategy: 选股策略
            output_format: 输出格式 (dataframe/csv/json)

        Returns:
            选股结果
        """
        # 获取所有股票列表
        stocks_df = self.data_client.get_stocks_list()

        if stocks_df.empty:
            return pd.DataFrame()

        # 筛选符合条件的股票
        results = []

        for _, row in stocks_df.iterrows():
            stock_code = row["code"]

            try:
                # 获取股票基本信息
                stock_info = self.data_client.get_stock_info(stock_code)

                # 获取最新财务数据
                financial_df = self.data_client.get_financial_data(stock_code)

                if financial_df.empty:
                    continue

                # 获取最新行情数据
                history_df = self.data_client.get_history_data(
                    stock_code,
                    "2023-01-01",
                    "2024-12-31",
                )

                if history_df.empty:
                    continue

                # 构建股票数据字典
                stock_data = {
                    "code": stock_info.code,
                    "name": stock_info.name,
                    "pe_ratio": None,
                    "pb_ratio": None,
                    "dividend_yield": None,
                    "roe": None,
                    "market_cap": None,
                }

                # 从财务数据提取指标
                latest_financial = financial_df.iloc[0]
                stock_data["pe_ratio"] = self._safe_float(latest_financial.get("roeAvg"))
                stock_data["roe"] = self._safe_float(latest_financial.get("roeAvg"))

                # 从行情数据计算市值和股息率
                latest_history = history_df.iloc[-1]
                stock_data["market_cap"] = self._safe_float(latest_history.get("volume"))

                # 检查所有条件
                if self._check_conditions(stock_data, strategy.conditions):
                    results.append(stock_data)

            except Exception as e:
                continue

        # 转换为 DataFrame
        result_df = pd.DataFrame(results)

        if result_df.empty:
            return result_df

        # 排序
        if strategy.sort_by and strategy.sort_by in result_df.columns:
            ascending = strategy.sort_order == "asc"
            result_df = result_df.sort_values(by=strategy.sort_by, ascending=ascending)

        # 限制结果数量
        if strategy.limit:
            result_df = result_df.head(strategy.limit)

        # 输出格式转换
        if output_format == "json":
            return result_df.to_dict(orient="records")
        elif output_format == "csv":
            return result_df.to_csv(index=False)
        else:
            return result_df

    def _check_conditions(
        self,
        stock_data: dict,
        conditions: List[Condition],
    ) -> bool:
        """检查股票是否满足所有条件"""
        series = pd.Series(stock_data)
        return all(c.applies_to(series) for c in conditions)

    def _safe_float(self, value: Any) -> Optional[float]:
        """安全转换为 float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    @classmethod
    def get_preset_strategy(cls, name: str) -> Optional[Strategy]:
        """
        获取预设策略

        Args:
            name: 策略名称 (high_dividend, low_valuation, blue_chip)

        Returns:
            预设策略，如果不存在返回 None
        """
        return cls.PRESET_STRATEGIES.get(name)

    @classmethod
    def list_preset_strategies(cls) -> list[str]:
        """列出所有预设策略"""
        return list(cls.PRESET_STRATEGIES.keys())
