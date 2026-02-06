#!/usr/bin/env python3
"""
A股股息率计算器 - 支持真实数据

基于五步法计算预期股息率：
1. 分类讨论（A/B/C/D类）
2. 测算基准
3. 行业基准纠正
4. 大股东需求纠正
5. 公告纠正

使用方法:
    python real_data_dividend_calculator.py --stock-code sh.600036 --price 41.2 --use-real-data
    python real_data_dividend_calculator.py --batch --use-real-data
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from enum import Enum

# 添加 finagent 包到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finagent.data.client import DataClient, DataClientConfig
from finagent.data.models.stock import StockInfo


class CompanyType(Enum):
    """公司分类类型"""
    A = "A"  # 业绩稳定 + 派息率稳定（银行、公用事业、电信、铁路、茅台等）
    B = "B"  # 业绩不稳定 + 派息率稳定（海运、白酒消费、煤、有色、化工等）
    C = "C"  # 业绩稳定 + 派息率不稳定（火电、部分油、水务、燃气、纺织、家电、高铁等）
    D = "D"  # 业绩不稳定 + 派息率不稳定（不建议新手投资）


@dataclass
class DividendRecord:
    """分红记录"""
    year: int
    eps: float  # 每股收益
    dividend_per_share: float  # 每股分红
    payout_ratio: float  # 派息率（百分比）


@dataclass
class CompanyData:
    """公司数据"""
    stock_code: str
    stock_name: str
    company_type: CompanyType
    current_price: float
    dividend_records: List[DividendRecord] = field(default_factory=list)
    industry: str = ""
    notes: str = ""


@dataclass
class AdjustmentFactors:
    """调整因子"""
    industry_adjustment: float = 0.0  # 行业基准纠正（百分比点）
    major_shareholder_adjustment: float = 0.0  # 大股东需求纠正（百分比点）
    announcement_adjustment: float = 0.0  # 公告纠正（百分比点）
    min_payout_ratio: Optional[float] = None  # 最低派息率（百分比）
    min_dividend_per_share: Optional[float] = None  # 最低每股分红


def fetch_company_data(data_client: DataClient, stock_code: str, current_price: float) -> Optional[CompanyData]:
    """
    从真实数据源获取公司数据

    Args:
        data_client: 数据客户端
        stock_code: 股票代码
        current_price: 当前股价

    Returns:
        公司数据，如果获取失败返回 None
    """
    try:
        # 获取股票基本信息
        stock_info = data_client.get_stock_info(stock_code)

        # 获取分红数据（最近5年）
        dividend_df = data_client.get_dividend_data(stock_code)

        if dividend_df.empty:
            print(f"⚠️  警告: 未获取到 {stock_code} 的分红数据")
            return None

        # 获取财务数据（用于计算EPS）
        financial_df = data_client.get_financial_data(stock_code)

        # 构建分红记录
        dividend_records = []
        for _, row in dividend_df.tail(5).iterrows():
            year = int(row.get("dividendYear", 0)) if row.get("dividendYear") else 0
            if year == 0:
                continue

            # 从财务数据获取EPS
            eps = 0.0
            if not financial_df.empty:
                year_financial = financial_df[financial_df.get("statDate", "").str.contains(str(year), na=False)]
                if not year_financial.empty:
                    eps_val = year_financial.iloc[0].get("epsTTM", 0)
                    eps = float(eps_val) if eps_val else 0.0

            # 获取分红数据
            dividend_ratio = row.get("dividendOperateRatio", 0)
            if dividend_ratio:
                dividend_ratio = float(dividend_ratio) / 10  # baostock 的单位是"每10股"

            # 计算派息率
            payout_ratio = (dividend_ratio / eps * 100) if eps > 0 else 0.0

            dividend_records.append(DividendRecord(
                year=year,
                eps=eps,
                dividend_per_share=dividend_ratio,
                payout_ratio=payout_ratio
            ))

        if not dividend_records:
            print(f"⚠️  警告: {stock_code} 没有有效的分红记录")
            return None

        # 确定公司类型（默认为A类，用户可以后续调整）
        company_type = CompanyType.A

        return CompanyData(
            stock_code=stock_code,
            stock_name=stock_info.name,
            company_type=company_type,
            current_price=current_price,
            dividend_records=dividend_records,
            industry=stock_info.industry or "未知"
        )

    except Exception as e:
        print(f"❌ 获取 {stock_code} 数据失败: {e}")
        return None


def calculate_payout_ratio_stability(records: List[DividendRecord]) -> Tuple[float, str]:
    """
    计算派息率稳定性

    稳定性等级：
    - 稳定：标准差 < 5%
    - 较稳定：标准差 5%-10%
    - 不稳定：标准差 > 10%
    """
    if len(records) < 2:
        return 0.0, "数据不足"

    payout_ratios = [r.payout_ratio for r in records if r.payout_ratio > 0]
    if not payout_ratios:
        return 0.0, "无有效数据"

    mean = sum(payout_ratios) / len(payout_ratios)
    variance = sum((x - mean) ** 2 for x in payout_ratios) / len(payout_ratios)
    std_dev = variance ** 0.5

    if std_dev < 5:
        return std_dev, "稳定"
    elif std_dev < 10:
        return std_dev, "较稳定"
    else:
        return std_dev, "不稳定"


def calculate_performance_stability(records: List[DividendRecord]) -> Tuple[float, str]:
    """
    计算业绩稳定性（基于每股收益变化率）

    稳定性等级：
    - 稳定：变化率标准差 < 10%
    - 较稳定：变化率标准差 10%-20%
    - 不稳定：变化率标准差 > 20%
    """
    if len(records) < 2:
        return 0.0, "数据不足"

    # 计算每年EPS变化率
    growth_rates = []
    for i in range(1, len(records)):
        if records[i - 1].eps > 0:
            growth_rate = (records[i].eps - records[i - 1].eps) / records[i - 1].eps * 100
            growth_rates.append(growth_rate)

    if not growth_rates:
        return 0.0, "数据不足"

    mean = sum(growth_rates) / len(growth_rates)
    variance = sum((x - mean) ** 2 for x in growth_rates) / len(growth_rates)
    std_dev = variance ** 0.5

    if std_dev < 10:
        return std_dev, "稳定"
    elif std_dev < 20:
        return std_dev, "较稳定"
    else:
        return std_dev, "不稳定"


def determine_company_type(performance_stability: str, payout_stability: str) -> CompanyType:
    """
    根据业绩稳定性和派息率稳定性确定公司类型
    """
    payout_stable = payout_stability in ["稳定", "较稳定"]
    performance_stable = performance_stability in ["稳定", "较稳定"]

    if performance_stable and payout_stable:
        return CompanyType.A
    elif not performance_stable and payout_stable:
        return CompanyType.B
    elif performance_stable and not payout_stable:
        return CompanyType.C
    else:
        return CompanyType.D


def calculate_expected_eps(records: List[DividendRecord]) -> float:
    """
    预测下一年每股收益

    方法：取最近年份的数据
    """
    if not records:
        return 0.0
    return records[-1].eps


def calculate_base_payout_ratio(records: List[DividendRecord], company_type: CompanyType) -> float:
    """
    计算基准派息率

    A类：取最近两年平均派息率
    B类：取最近两年平均派息率
    C类：取最近两年平均派息率
    D类：不推荐计算
    """
    if not records:
        return 0.0

    # 取最近两年数据
    recent_records = sorted(records, key=lambda x: x.year, reverse=True)[:2]
    valid_records = [r for r in recent_records if r.payout_ratio > 0]

    if len(valid_records) < 2:
        return valid_records[0].payout_ratio if valid_records else 0.0

    avg_payout = sum(r.payout_ratio for r in valid_records) / len(valid_records)
    return avg_payout


def calculate_base_dividend_yield(
    company_data: CompanyData,
    expected_eps: float,
    base_payout_ratio: float
) -> float:
    """
    计算基准预期股息率

    公式：预期每股分红 = 预期EPS * 基准派息率
          预期股息率 = 预期每股分红 / 当前股价
    """
    if company_data.current_price <= 0:
        return 0.0

    expected_dividend = expected_eps * base_payout_ratio / 100
    dividend_yield = expected_dividend / company_data.current_price * 100
    return dividend_yield


def apply_industry_adjustment(
    base_yield: float,
    company_type: CompanyType,
    adjustment_factors: AdjustmentFactors,
    base_payout_ratio: float
) -> float:
    """
    应用行业基准纠正
    """
    adjusted_payout = base_payout_ratio + adjustment_factors.industry_adjustment
    adjusted_yield = base_yield * (adjusted_payout / base_payout_ratio) if base_payout_ratio > 0 else base_yield
    return adjusted_yield


def apply_major_shareholder_adjustment(
    current_yield: float,
    company_type: CompanyType,
    adjustment_factors: AdjustmentFactors,
    base_payout_ratio: float
) -> float:
    """
    应用大股东需求纠正
    """
    adjusted_payout = base_payout_ratio + adjustment_factors.major_shareholder_adjustment
    adjusted_yield = current_yield * (adjusted_payout / base_payout_ratio) if base_payout_ratio > 0 else current_yield
    return adjusted_yield


def apply_announcement_adjustment(
    company_data: CompanyData,
    current_yield: float,
    expected_eps: float,
    adjustment_factors: AdjustmentFactors
) -> Tuple[float, str]:
    """
    应用公告纠正
    """
    notes = []

    if adjustment_factors.min_payout_ratio is not None:
        # 最低派息率约束
        min_dividend = expected_eps * adjustment_factors.min_payout_ratio / 100
        min_yield = min_dividend / company_data.current_price * 100
        notes.append(f"最低派息率约束：{adjustment_factors.min_payout_ratio}%")

        if adjustment_factors.min_dividend_per_share is not None:
            # 最低每股分红约束
            min_yield_from_div = adjustment_factors.min_dividend_per_share / company_data.current_price * 100
            notes.append(f"最低每股分红：{adjustment_factors.min_dividend_per_share}元")

            # 取两者中的较高值
            final_yield = max(min_yield, min_yield_from_div)
            return final_yield, "; ".join(notes)

        return max(current_yield, min_yield), "; ".join(notes)

    if adjustment_factors.min_dividend_per_share is not None:
        min_yield = adjustment_factors.min_dividend_per_share / company_data.current_price * 100
        notes.append(f"最低每股分红：{adjustment_factors.min_dividend_per_share}元")
        return max(current_yield, min_yield), "; ".join(notes)

    # 如果没有公告约束，应用调整因子
    if adjustment_factors.announcement_adjustment != 0:
        notes.append(f"公告调整：{adjustment_factors.announcement_adjustment:+.1f}%")
        return current_yield + adjustment_factors.announcement_adjustment, "; ".join(notes)

    return current_yield, ""


def calculate_dividend_yield(
    company_data: CompanyData,
    adjustment_factors: Optional[AdjustmentFactors] = None
) -> Dict:
    """
    计算预期股息率（完整流程）

    Returns:
        包含计算结果和详细步骤的字典
    """
    if adjustment_factors is None:
        adjustment_factors = AdjustmentFactors()

    records = company_data.dividend_records
    if not records:
        return {
            "error": "缺少分红数据",
            "stock_code": company_data.stock_code,
            "stock_name": company_data.stock_name
        }

    # 第一步：分类讨论
    payout_std, payout_stability = calculate_payout_ratio_stability(records)
    perf_std, perf_stability = calculate_performance_stability(records)

    # 自动判断公司类型
    company_data.company_type = determine_company_type(perf_stability, payout_stability)

    # 第二步：测算基准
    expected_eps = calculate_expected_eps(records)
    base_payout_ratio = calculate_base_payout_ratio(records, company_data.company_type)
    base_yield = calculate_base_dividend_yield(company_data, expected_eps, base_payout_ratio)

    result = {
        "stock_code": company_data.stock_code,
        "stock_name": company_data.stock_name,
        "company_type": company_data.company_type.value,
        "current_price": company_data.current_price,
        "expected_eps": round(expected_eps, 2),
        "base_payout_ratio": round(base_payout_ratio, 2),
        "base_yield": round(base_yield, 2),
        "payout_stability": payout_stability,
        "payout_std": round(payout_std, 2),
        "performance_stability": perf_stability,
        "performance_std": round(perf_std, 2),
        "steps": []
    }

    # 第三步：行业基准纠正
    after_industry = apply_industry_adjustment(
        base_yield, company_data.company_type, adjustment_factors, base_payout_ratio
    )
    result["steps"].append({
        "step": "行业基准纠正",
        "yield": round(after_industry, 2),
        "adjustment": round(after_industry - base_yield, 2),
        "note": adjustment_factors.industry_adjustment
    })

    # 第四步：大股东需求纠正
    after_shareholder = apply_major_shareholder_adjustment(
        after_industry, company_data.company_type, adjustment_factors, base_payout_ratio
    )
    result["steps"].append({
        "step": "大股东需求纠正",
        "yield": round(after_shareholder, 2),
        "adjustment": round(after_shareholder - after_industry, 2),
        "note": adjustment_factors.major_shareholder_adjustment
    })

    # 第五步：公告纠正
    final_yield, announcement_note = apply_announcement_adjustment(
        company_data, after_shareholder, expected_eps, adjustment_factors
    )
    result["steps"].append({
        "step": "公告纠正",
        "yield": round(final_yield, 2),
        "adjustment": round(final_yield - after_shareholder, 2),
        "note": announcement_note or adjustment_factors.announcement_adjustment
    })

    result["final_yield"] = round(final_yield, 2)
    result["total_adjustment"] = round(final_yield - base_yield, 2)

    return result


def format_result(result: Dict) -> str:
    """格式化输出结果"""
    if "error" in result:
        return f"❌ {result['stock_code']} {result.get('stock_name', '')}: {result['error']}"

    lines = [
        f"\n{'='*60}",
        f"📊 {result['stock_name']} ({result['stock_code']})",
        f"{'='*60}",
        f"公司类型: {result['company_type']}类",
        f"当前股价: {result['current_price']:.2f}元",
        f"预期EPS: {result['expected_eps']:.2f}元",
        f"基准派息率: {result['base_payout_ratio']:.2f}%",
        f"",
        f"稳定性指标:",
        f"  派息率稳定性: {result['payout_stability']} (标准差: {result['payout_std']:.2f}%)",
        f"  业绩稳定性: {result['performance_stability']} (标准差: {result['performance_std']:.2f}%)",
        f"",
        f"股息率计算步骤:",
        f"  1. 基准预期股息率: {result['base_yield']:.2f}%",
    ]

    for step in result["steps"]:
        adj_str = f" ({step['adjustment']:+.2f}%)" if step['adjustment'] != 0 else ""
        lines.append(f"  2. {step['step']}: {step['yield']:.2f}%{adj_str}")

    lines.extend([
        f"",
        f"🎯 最终预期股息率: {result['final_yield']:.2f}%",
        f"📈 总调整幅度: {result['total_adjustment']:+.2f}%",
        f"{'='*60}"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="A股股息率计算器 - 支持真实数据")
    parser.add_argument("--stock-code", help="股票代码 (如 sh.600036)")
    parser.add_argument("--price", type=float, help="当前股价")
    parser.add_argument("--use-real-data", action="store_true", help="使用真实数据源（baostock）")
    parser.add_argument("--batch", action="store_true", help="批量计算示例")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    if args.use_real_data:
        # 使用真实数据源
        config = DataClientConfig(
            provider="baostock",
            enable_cache=True,
            rate_limit=1.0,
        )
        data_client = DataClient(config)

        print("🔄 正在连接数据源...")

        if args.stock_code and args.price:
            # 单个股票计算
            company_data = fetch_company_data(data_client, args.stock_code, args.price)
            if company_data:
                result = calculate_dividend_yield(company_data)

                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(format_result(result))

                # 显示缓存统计
                stats = data_client.get_cache_stats()
                print(f"\n📦 缓存统计: 命中率 {stats.get('hit_rate', 0)*100:.1f}%")
            else:
                print(f"❌ 无法获取 {args.stock_code} 的数据")
        else:
            parser.print_help()

        data_client.close()
    else:
        print("❌ 请使用 --use-real-data 参数启用真实数据源")
        print("提示: 确保已安装 baostock: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
