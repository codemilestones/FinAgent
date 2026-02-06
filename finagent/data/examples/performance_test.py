#!/usr/bin/env python3
"""
FinAgent 性能测试脚本

测试数据获取、缓存和批量查询的性能。
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加 finagent 包到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finagent.data.client import DataClient, DataClientConfig


def test_single_query_performance():
    """测试单个查询性能"""
    print("\n" + "=" * 60)
    print("性能测试 1: 单个查询")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 第一次查询（未命中缓存）
        start = time.time()
        stock_info = client.get_stock_info("sh.600036")
        elapsed_first = time.time() - start
        print(f"第一次查询（未命中缓存）: {elapsed_first:.3f} 秒")

        # 第二次查询（命中缓存）
        start = time.time()
        stock_info = client.get_stock_info("sh.600036")
        elapsed_cached = time.time() - start
        print(f"第二次查询（命中缓存）: {elapsed_cached:.3f} 秒")

        # 计算加速比
        if elapsed_cached > 0:
            speedup = elapsed_first / elapsed_cached
            print(f"缓存加速比: {speedup:.1f}x")

    finally:
        client.close()


def test_batch_query_performance():
    """测试批量查询性能"""
    print("\n" + "=" * 60)
    print("性能测试 2: 批量查询")
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

        # 测试不同批量大小的性能
        batch_sizes = [10, 20, 50]

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        for batch_size in batch_sizes:
            sample_codes = stocks_df['code'].head(batch_size).tolist()

            start = time.time()
            history_data = client.get_batch_history_data(
                stock_codes=sample_codes,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
            )
            elapsed = time.time() - start

            print(f"批量 {batch_size} 只股票: {elapsed:.2f} 秒 ({elapsed/batch_size:.3f} 秒/股)")

    finally:
        client.close()


def test_cache_effectiveness():
    """测试缓存效果"""
    print("\n" + "=" * 60)
    print("性能测试 3: 缓存效果")
    print("=" * 60)

    # 先清空缓存
    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)
    client.clear_cache()
    client.close()

    # 第一次运行（无缓存）
    client = DataClient(config)

    start = time.time()
    for code in ["sh.600036", "sh.600000", "sz.000001"]:
        client.get_stock_info(code)
    elapsed_no_cache = time.time() - start
    print(f"无缓存查询 3 只股票: {elapsed_no_cache:.2f} 秒")

    stats = client.get_cache_stats()
    print(f"  缓存命中: {stats['hits']}/{stats['total']}")

    client.close()

    # 第二次运行（有缓存）
    client = DataClient(config)

    start = time.time()
    for code in ["sh.600036", "sh.600000", "sz.000001"]:
        client.get_stock_info(code)
    elapsed_with_cache = time.time() - start
    print(f"有缓存查询 3 只股票: {elapsed_with_cache:.2f} 秒")

    stats = client.get_cache_stats()
    print(f"  缓存命中: {stats['hits']}/{stats['total']}")

    # 计算加速比
    if elapsed_with_cache > 0:
        speedup = elapsed_no_cache / elapsed_with_cache
        print(f"  总体加速比: {speedup:.1f}x")

    client.close()


def test_data_query_performance():
    """测试不同数据类型的查询性能"""
    print("\n" + "=" * 60)
    print("性能测试 4: 不同数据类型查询")
    print("=" * 60)

    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        code = "sh.600036"

        # 股票基本信息
        start = time.time()
        stock_info = client.get_stock_info(code)
        elapsed = time.time() - start
        print(f"股票基本信息: {elapsed:.3f} 秒")

        # 历史行情数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        start = time.time()
        history_df = client.get_history_data(code, start_date, end_date, "d")
        elapsed = time.time() - start
        print(f"历史行情数据 (30天): {elapsed:.3f} 秒 ({len(history_df)} 条记录)")

        # 分红数据
        start = time.time()
        dividend_df = client.get_dividend_data(code)
        elapsed = time.time() - start
        print(f"分红数据: {elapsed:.3f} 秒 ({len(dividend_df)} 条记录)")

        # 财务数据
        start = time.time()
        financial_df = client.get_financial_data(code)
        elapsed = time.time() - start
        print(f"财务数据: {elapsed:.3f} 秒 ({len(financial_df)} 条记录)")

    finally:
        client.close()


def test_cache_size_impact():
    """测试缓存大小对性能的影响"""
    print("\n" + "=" * 60)
    print("性能测试 5: 缓存大小影响")
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
        sample_codes = stocks_df['code'].head(100).tolist()

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # 首次填充缓存
        print("填充缓存...")
        start = time.time()
        history_data = client.get_batch_history_data(
            stock_codes=sample_codes,
            start_date=start_date,
            end_date=end_date,
            frequency="d",
        )
        elapsed = time.time() - start
        print(f"填充 100 只股票缓存: {elapsed:.2f} 秒")

        stats = client.get_cache_stats()
        print(f"缓存大小: {stats['cache_size']} 条")
        print(f"命中率: {stats['hit_rate']*100:.1f}%")

    finally:
        client.close()


def main():
    """运行所有性能测试"""
    print("\n" + "=" * 60)
    print("FinAgent 性能测试")
    print("=" * 60)
    print("\n提示: 这些测试需要连接 baostock 数据源")
    print("      首次运行可能需要较长时间")

    tests = [
        test_single_query_performance,
        test_cache_effectiveness,
        test_data_query_performance,
        test_batch_query_performance,
        test_cache_size_impact,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("性能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
