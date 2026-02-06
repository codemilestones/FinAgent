#!/usr/bin/env python3
"""
A股高股息率标的批量分析脚本

根据A股市场特点，分析以下高股息行业：
1. 银行股（A类）
2. 公用事业（A类）
3. 能源煤炭（A类）
4. 电信运营（A类）
5. 高速公路（A类）
6. 白酒龙头（A类）
"""

import sys
import os

# 添加父目录到路径以导入dividend_calculator
sys.path.insert(0, os.path.dirname(__file__))

from dividend_calculator import (
    CompanyData, DividendRecord, CompanyType,
    AdjustmentFactors, calculate_dividend_yield, format_result
)


# A股高股息率标的池（基于2024-2025年市场数据）
HIGH_DIVIDEND_STOCKS = {
    # ===== 银行股（A类：业绩稳定+派息率稳定）=====
    "601398": {
        "stock_code": "601398",
        "stock_name": "工商银行",
        "company_type": CompanyType.A,
        "current_price": 5.68,
        "industry": "银行",
        "notes": "宇宙行，业绩稳定，派息率约30%",
        "dividend_records": [
            DividendRecord(2022, 0.97, 0.29, 30.18),
            DividendRecord(2023, 0.98, 0.30, 30.61),
            DividendRecord(2024, 1.01, 0.31, 30.69),
        ]
    },
    "601939": {
        "stock_code": "601939",
        "stock_name": "建设银行",
        "company_type": CompanyType.A,
        "current_price": 6.85,
        "industry": "银行",
        "notes": "派息率稳定在30%左右",
        "dividend_records": [
            DividendRecord(2022, 1.23, 0.39, 31.71),
            DividendRecord(2023, 1.28, 0.40, 31.25),
            DividendRecord(2024, 1.32, 0.41, 31.06),
        ]
    },
    "601288": {
        "stock_code": "601288",
        "stock_name": "农业银行",
        "company_type": CompanyType.A,
        "current_price": 4.12,
        "industry": "银行",
        "notes": "派息率稳定在30%以上",
        "dividend_records": [
            DividendRecord(2022, 0.70, 0.22, 31.43),
            DividendRecord(2023, 0.72, 0.23, 31.94),
            DividendRecord(2024, 0.75, 0.24, 32.00),
        ]
    },
    "601988": {
        "stock_code": "601988",
        "stock_name": "中国银行",
        "company_type": CompanyType.A,
        "current_price": 4.58,
        "industry": "银行",
        "notes": "派息率约30%",
        "dividend_records": [
            DividendRecord(2022, 0.75, 0.23, 30.67),
            DividendRecord(2023, 0.78, 0.24, 30.77),
            DividendRecord(2024, 0.82, 0.25, 30.49),
        ]
    },
    "600036": {
        "stock_code": "600036",
        "stock_name": "招商银行",
        "company_type": CompanyType.A,
        "current_price": 33.50,
        "industry": "银行",
        "notes": "零售银行龙头，业绩优秀",
        "dividend_records": [
            DividendRecord(2022, 5.26, 1.74, 33.08),
            DividendRecord(2023, 5.66, 1.92, 33.92),
            DividendRecord(2024, 5.60, 1.90, 33.93),
        ]
    },

    # ===== 公用事业（A类）=====
    "600900": {
        "stock_code": "600900",
        "stock_name": "长江电力",
        "company_type": CompanyType.A,
        "current_price": 26.50,
        "industry": "水电",
        "notes": "水电龙头，承诺高比例分红",
        "dividend_records": [
            DividendRecord(2022, 1.14, 0.85, 74.56),
            DividendRecord(2023, 1.32, 1.00, 75.76),
            DividendRecord(2024, 1.40, 1.05, 75.00),
        ]
    },
    "600011": {
        "stock_code": "600011",
        "stock_name": "华能国际",
        "company_type": CompanyType.C,
        "current_price": 8.20,
        "industry": "火电",
        "notes": "火电龙头，派息率不稳定（煤价影响）",
        "dividend_records": [
            DividendRecord(2022, -0.12, 0.0, 0.0),
            DividendRecord(2023, 0.65, 0.25, 38.46),
            DividendRecord(2024, 0.92, 0.35, 38.04),
        ]
    },

    # ===== 能源煤炭（A类）=====
    "601088": {
        "stock_code": "601088",
        "stock_name": "中国神华",
        "company_type": CompanyType.A,
        "current_price": 42.80,
        "industry": "煤炭",
        "notes": "煤炭龙头，高股息率典范",
        "dividend_records": [
            DividendRecord(2022, 3.50, 2.55, 72.86),
            DividendRecord(2023, 2.62, 2.26, 86.26),
            DividendRecord(2024, 2.85, 2.40, 84.21),
        ]
    },
    "601225": {
        "stock_code": "601225",
        "stock_name": "陕西煤业",
        "company_type": CompanyType.A,
        "current_price": 24.50,
        "industry": "煤炭",
        "notes": "优质煤企，高分红",
        "dividend_records": [
            DividendRecord(2022, 3.54, 2.18, 61.58),
            DividendRecord(2023, 2.18, 1.35, 61.93),
            DividendRecord(2024, 2.45, 1.50, 61.22),
        ]
    },

    # ===== 电信运营（A类）=====
    "600941": {
        "stock_code": "600941",
        "stock_name": "中国移动",
        "company_type": CompanyType.A,
        "current_price": 108.00,
        "industry": "电信",
        "notes": "电信龙头，派息率逐步提升",
        "dividend_records": [
            DividendRecord(2022, 5.88, 3.02, 51.36),
            DividendRecord(2023, 6.26, 3.50, 55.91),
            DividendRecord(2024, 6.65, 3.80, 57.14),
        ]
    },
    "601728": {
        "stock_code": "601728",
        "stock_name": "中国电信",
        "company_type": CompanyType.A,
        "current_price": 5.95,
        "industry": "电信",
        "notes": "派息率稳定提升",
        "dividend_records": [
            DividendRecord(2022, 0.25, 0.12, 48.00),
            DividendRecord(2023, 0.31, 0.16, 51.61),
            DividendRecord(2024, 0.35, 0.19, 54.29),
        ]
    },

    # ===== 高速公路（A类）=====
    "600377": {
        "stock_code": "600377",
        "stock_name": "宁沪高速",
        "company_type": CompanyType.A,
        "current_price": 10.80,
        "industry": "高速公路",
        "notes": "现金流稳定，高分红",
        "dividend_records": [
            DividendRecord(2022, 0.76, 0.46, 60.53),
            DividendRecord(2023, 0.82, 0.50, 60.98),
            DividendRecord(2024, 0.88, 0.54, 61.36),
        ]
    },

    # ===== 白酒龙头（A类）=====
    "600519": {
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "company_type": CompanyType.A,
        "current_price": 1680.00,
        "industry": "白酒",
        "notes": "白酒龙头，特殊分红",
        "dividend_records": [
            DividendRecord(2022, 49.93, 25.91, 51.89),
            DividendRecord(2023, 59.31, 30.87, 52.05),
            DividendRecord(2024, 65.50, 34.50, 52.67),
        ]
    },
    "000858": {
        "stock_code": "000858",
        "stock_name": "五粮液",
        "company_type": CompanyType.A,
        "current_price": 125.00,
        "industry": "白酒",
        "notes": "承诺分红率不低于70%",
        "dividend_records": [
            DividendRecord(2022, 6.90, 4.80, 69.57),
            DividendRecord(2023, 7.36, 5.15, 70.0),
            DividendRecord(2024, 7.00, 4.90, 70.0),
        ]
    },

    # ===== 其他高股息标的 =====
    "600585": {
        "stock_code": "600585",
        "stock_name": "海螺水泥",
        "company_type": CompanyType.B,
        "current_price": 28.50,
        "industry": "水泥",
        "notes": "周期股，派息率稳定",
        "dividend_records": [
            DividendRecord(2022, 2.88, 1.68, 58.33),
            DividendRecord(2023, 1.95, 1.12, 57.44),
            DividendRecord(2024, 2.10, 1.20, 57.14),
        ]
    },
    "601872": {
        "stock_code": "601872",
        "stock_name": "招商轮船",
        "company_type": CompanyType.B,
        "current_price": 7.85,
        "industry": "海运",
        "notes": "油运周期股",
        "dividend_records": [
            DividendRecord(2022, 0.48, 0.16, 33.33),
            DividendRecord(2023, 0.65, 0.22, 33.85),
            DividendRecord(2024, 0.58, 0.19, 32.76),
        ]
    },
}


def get_adjustment_factors(stock_code: str) -> AdjustmentFactors:
    """获取特定股票的调整因子"""
    # 五粮液有特殊分红承诺
    if stock_code == "000858":
        return AdjustmentFactors(
            min_payout_ratio=70.0,
            min_dividend_per_share=5.15
        )

    # 长江电力有高分红承诺
    if stock_code == "600900":
        return AdjustmentFactors(
            min_payout_ratio=70.0,
            industry_adjustment=2.0  # 水电行业现金流稳定，适当上调
        )

    # 中国神华保持高分红
    if stock_code == "601088":
        return AdjustmentFactors(
            min_payout_ratio=75.0,
            industry_adjustment=2.0
        )

    # 中国移动承诺提升分红率
    if stock_code == "600941":
        return AdjustmentFactors(
            announcement_adjustment=1.0  # 公司承诺逐步提升分红率至70%+
        )

    return AdjustmentFactors()


def batch_analyze():
    """批量分析所有高股息标的"""
    print("\n" + "="*80)
    print("A股高股息率标的批量分析")
    print("="*80)
    print(f"分析标的数量: {len(HIGH_DIVIDEND_STOCKS)} 只")
    print("="*80 + "\n")

    results = []

    for code, data in HIGH_DIVIDEND_STOCKS.items():
        company = CompanyData(**data)
        factors = get_adjustment_factors(code)
        result = calculate_dividend_yield(company, factors)
        results.append(result)

    # 按预期股息率排序
    results_sorted = sorted(results, key=lambda x: x.get("final_yield", 0), reverse=True)

    # 输出汇总表
    print("\n" + "="*80)
    print("📊 预期股息率排行榜（TOP 15）")
    print("="*80)
    print(f"{'排名':<4} {'代码':<8} {'名称':<10} {'类型':<4} {'当前股价':<10} {'预期股息率':<10} {'派息稳定性':<10} {'业绩稳定性':<10}")
    print("-"*80)

    for i, result in enumerate(results_sorted[:15], 1):
        print(f"{i:<4} {result['stock_code']:<8} {result['stock_name']:<10} "
              f"{result['company_type']}类  {result['current_price']:<10.2f} "
              f"{result['final_yield']:<10.2f}% {result['payout_stability']:<10} "
              f"{result['performance_stability']:<10}")

    print("="*80)

    # 输出详细分析
    print("\n\n" + "="*80)
    print("📋 详细分析报告")
    print("="*80)

    for result in results_sorted:
        print(format_result(result))
        print()

    # 统计分析
    print("\n" + "="*80)
    print("📈 统计分析")
    print("="*80)

    type_counts = {}
    for r in results:
        t = r['company_type']
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"公司类型分布:")
    for t, count in sorted(type_counts.items()):
        print(f"  {t}类: {count} 只")

    avg_yield = sum(r['final_yield'] for r in results) / len(results)
    print(f"\n平均预期股息率: {avg_yield:.2f}%")

    high_yield_count = sum(1 for r in results if r['final_yield'] >= 5.0)
    print(f"股息率≥5%的标的: {high_yield_count} 只 ({high_yield_count/len(results)*100:.1f}%)")

    stable_count = sum(1 for r in results if r['payout_stability'] == '稳定' and r['performance_stability'] == '稳定')
    print(f"双稳定标的（派息+业绩均稳定）: {stable_count} 只")

    print("="*80 + "\n")

    # 推荐标的
    print("\n" + "="*80)
    print("🌟 推荐标的（高股息率 + 高稳定性）")
    print("="*80)

    recommended = [
        r for r in results
        if r['final_yield'] >= 4.5
        and r['payout_stability'] in ['稳定', '较稳定']
        and r['performance_stability'] in ['稳定', '较稳定']
    ]

    recommended = sorted(recommended, key=lambda x: x['final_yield'], reverse=True)

    print(f"\n共找到 {len(recommended)} 只符合条件的高质量高股息标的:\n")

    for i, r in enumerate(recommended, 1):
        print(f"{i}. {r['stock_name']} ({r['stock_code']}) - {r['company_type']}类")
        print(f"   当前股价: {r['current_price']:.2f}元 | 预期股息率: {r['final_yield']:.2f}%")
        print(f"   派息稳定性: {r['payout_stability']} | 业绩稳定性: {r['performance_stability']}")
        print(f"   基准派息率: {r['base_payout_ratio']:.2f}%")
        print()

    print("="*80 + "\n")

    return results_sorted


if __name__ == "__main__":
    batch_analyze()
