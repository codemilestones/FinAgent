#!/usr/bin/env python3
"""
FinAgent 数据基础设施使用示例

本示例展示如何使用 FinAgent 的数据层进行各种操作：
- 获取股票基本信息
- 获取历史行情数据
- 获取分红数据
- 获取财务数据
- 批量查询
- 选股条件筛选
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加 finagent 包到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finagent.data.client import DataClient, DataClientConfig
from finagent.data.criteria.condition import (
    Condition, Operator, StrategyExecutor,
    PresetStrategy
)


def example_1_basic_info():
    """示例 1: 获取股票基本信息"""
    print("\n" + "=" * 60)
    print("示例 1: 获取股票基本信息")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 获取招商银行基本信息
        stock_info = client.get_stock_info("sh.600036")

        print(f"股票代码: {stock_info.code}")
        print(f"股票名称: {stock_info.name}")
        print(f"上市日期: {stock_info.ipo_date}")
        print(f"行业: {stock_info.industry or '未知'}")

    finally:
        client.close()


def example_2_history_data():
    """示例 2: 获取历史行情数据"""
    print("\n" + "=" * 60)
    print("示例 2: 获取历史行情数据")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 获取最近 30 天的行情数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        history_df = client.get_history_data(
            stock_code="sh.600036",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            frequency="d",  # d=日k线, w=周, m=月
        )

        if not history_df.empty:
            print(f"获取到 {len(history_df)} 条记录")
            print("\n最新 5 条记录:")
            print(history_df[['date', 'open', 'high', 'low', 'close', 'volume']].tail())

            # 计算简单统计
            print(f"\n期间最高价: {history_df['high'].max():.2f}")
            print(f"期间最低价: {history_df['low'].min():.2f}")
            print(f"期间平均收盘价: {history_df['close'].mean():.2f}")
        else:
            print("未获取到数据")

    finally:
        client.close()


def example_3_dividend_data():
    """示例 3: 获取分红数据"""
    print("\n" + "=" * 60)
    print("示例 3: 获取分红数据")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        dividend_df = client.get_dividend_data("sh.600036")

        if not dividend_df.empty:
            print(f"获取到 {len(dividend_df)} 条分红记录")
            print("\n最近 5 条分红记录:")
            print(dividend_df.tail())
        else:
            print("未获取到分红数据")

    finally:
        client.close()


def example_4_financial_data():
    """示例 4: 获取财务数据"""
    print("\n" + "=" * 60)
    print("示例 4: 获取财务数据")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        financial_df = client.get_financial_data("sh.600036")

        if not financial_df.empty:
            print(f"获取到 {len(financial_df)} 条财务记录")
            print("\n最近 5 条财务记录:")

            # 只显示关键指标
            key_columns = ["statDate", "roeAvg", "epsTTM", "netProfit", "totalAssets"]
            available_columns = [col for col in key_columns if col in financial_df.columns]
            if available_columns:
                print(financial_df[available_columns].tail())
            else:
                print(financial_df.tail())
        else:
            print("未获取到财务数据")

    finally:
        client.close()


def example_5_batch_query():
    """示例 5: 批量查询多只股票"""
    print("\n" + "=" * 60)
    print("示例 5: 批量查询多只股票")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        stock_codes = ["sh.600036", "sh.600000", "sz.000001"]

        # 批量获取基本信息
        print("批量获取股票基本信息:")
        for code in stock_codes:
            try:
                stock_info = client.get_stock_info(code)
                print(f"  {stock_info.code} - {stock_info.name} ({stock_info.industry or '未知'})")
            except Exception as e:
                print(f"  {code} - 获取失败: {e}")

        # 显示缓存效果
        stats = client.get_cache_stats()
        print(f"\n缓存命中率: {stats['hit_rate'] * 100:.1f}%")

    finally:
        client.close()


def example_6_stock_selection():
    """示例 6: 使用选股条件筛选"""
    print("\n" + "=" * 60)
    print("示例 6: 使用选股条件筛选")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 获取股票列表
        stocks_df = client.get_stocks_list()
        print(f"获取到 {len(stocks_df)} 只股票")

        # 取前 100 只股票作为示例
        sample_codes = stocks_df['code'].head(100).tolist()

        # 批量获取行情数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n获取最近 30 天的行情数据...")
        history_data = client.get_batch_history_data(
            stock_codes=sample_codes,
            start_date=start_date,
            end_date=end_date,
            frequency="d",
        )

        # 使用选股条件筛选：找高价股（最新收盘价 > 50）
        executor = StrategyExecutor()

        strategy = {
            "name": "高价股策略",
            "conditions": [
                Condition(field="close", operator=Operator.GREATER_THAN, value=50),
            ],
            "sort_by": "close",
            "sort_order": "desc",
            "limit": 10,
        }

        results = executor.execute(history_data, strategy)

        print(f"\n筛选结果: {len(results)} 只股票")
        print(results[['code', "close", "volume"]].to_string(index=False))

    except Exception as e:
        print(f"选股失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


def example_7_preset_strategies():
    """示例 7: 使用预设策略"""
    print("\n" + "=" * 60)
    print("示例 7: 使用预设策略")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 获取股票列表
        stocks_df = client.get_stocks_list()
        sample_codes = stocks_df['code'].head(50).tolist()

        # 批量获取数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        history_data = client.get_batch_history_data(
            stock_codes=sample_codes,
            start_date=start_date,
            end_date=end_date,
            frequency="d",
        )

        # 使用预设的高股息策略
        executor = StrategyExecutor()
        strategy = PresetStrategy.high_dividend()

        results = executor.execute(history_data, strategy)

        print(f"\n高股息策略筛选结果: {len(results)} 只股票")
        if not results.empty:
            print(results.head(10).to_string(index=False))

    except Exception as e:
        print(f"策略执行失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


def example_8_cache_management():
    """示例 8: 缓存管理"""
    print("\n" + "=" * 60)
    print("示例 8: 缓存管理")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
        cache_ttl=3600,  # 1 小时缓存
    )
    client = DataClient(config)

    try:
        # 第一次查询
        print("第一次查询（未命中缓存）:")
        stock_info = client.get_stock_info("sh.600036")
        print(f"  股票名称: {stock_info.name}")

        stats = client.get_cache_stats()
        print(f"  缓存命中率: {stats['hit_rate'] * 100:.1f}%")

        # 第二次查询（应该命中缓存）
        print("\n第二次查询（命中缓存）:")
        stock_info = client.get_stock_info("sh.600036")
        print(f"  股票名称: {stock_info.name}")

        stats = client.get_cache_stats()
        print(f"  缓存命中率: {stats['hit_rate'] * 100:.1f}%")

        # 清空缓存
        print("\n清空缓存...")
        client.clear_cache()

        stats = client.get_cache_stats()
        print(f"  缓存大小: {stats['cache_size']} 条")

    finally:
        client.close()


def main():
    """运行所有示例"""
    examples = [
        ("获取股票基本信息", example_1_basic_info),
        ("获取历史行情数据", example_2_history_data),
        ("获取分红数据", example_3_dividend_data),
        ("获取财务数据", example_4_financial_data),
        ("批量查询多只股票", example_5_batch_query),
        ("使用选股条件筛选", example_6_stock_selection),
        ("使用预设策略", example_7_preset_strategies),
        ("缓存管理", example_8_cache_management),
    ]

    print("\n" + "=" * 60)
    print("FinAgent 数据基础设施使用示例")
    print("=" * 60)
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n提示: 这些示例需要连接 baostock 数据源")
    print("      首次运行可能需要较长时间来下载和缓存数据")

    # 运行所有示例
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ 示例 '{name}' 执行失败: {e}")

    print("\n" + "=" * 60)
    print("所有示例执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
