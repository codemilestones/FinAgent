#!/usr/bin/env python3
"""
获取最近30天的股票数据示例

使用方法:
    python fetch_recent_data.py --stock-code sh.600036
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 finagent 包到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finagent.data.client import DataClient, DataClientConfig


def main():
    parser = argparse.ArgumentParser(description="获取最近30天的股票数据")
    parser.add_argument("--stock-code", default="sh.600036", help="股票代码 (默认: sh.600036 招商银行)")
    args = parser.parse_args()

    # 计算日期范围（最近30天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"🔄 正在获取 {args.stock_code} 的数据...")
    print(f"📅 日期范围: {start_date_str} 至 {end_date_str}")
    print("=" * 60)

    # 创建数据客户端
    config = DataClientConfig(
        provider="baostock",
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    try:
        # 1. 获取股票基本信息
        print("\n📊 1. 股票基本信息")
        print("-" * 40)
        stock_info = client.get_stock_info(args.stock_code)
        print(f"股票代码: {stock_info.code}")
        print(f"股票名称: {stock_info.name}")
        print(f"上市日期: {stock_info.ipo_date}")
        print(f"行业: {stock_info.industry or '未知'}")

        # 2. 获取历史行情数据
        print(f"\n📈 2. 历史行情数据 (最近30天)")
        print("-" * 40)
        history_df = client.get_history_data(
            stock_code=args.stock_code,
            start_date=start_date_str,
            end_date=end_date_str,
            frequency="d",
        )

        if not history_df.empty:
            print(f"获取到 {len(history_df)} 条记录")
            print("\n最新5条记录:")
            print(history_df.tail().to_string(index=False))

            # 统计信息
            print(f"\n统计信息:")
            print(f"  最高价: {history_df['high'].max():.2f}")
            print(f"  最低价: {history_df['low'].min():.2f}")
            print(f"  平均收盘价: {history_df['close'].mean():.2f}")
            print(f"  期间涨跌: {((history_df['close'].iloc[-1] - history_df['close'].iloc[0]) / history_df['close'].iloc[0] * 100):.2f}%")
        else:
            print("⚠️  未获取到历史行情数据")

        # 3. 获取分红数据
        print(f"\n💰 3. 分红数据")
        print("-" * 40)
        dividend_df = client.get_dividend_data(args.stock_code)

        if not dividend_df.empty:
            print(f"获取到 {len(dividend_df)} 条记录")
            print("\n最近5条分红记录:")
            print(dividend_df.tail().to_string(index=False))
        else:
            print("⚠️  未获取到分红数据")

        # 4. 获取财务数据
        print(f"\n💼 4. 财务数据")
        print("-" * 40)
        financial_df = client.get_financial_data(args.stock_code)

        if not financial_df.empty:
            print(f"获取到 {len(financial_df)} 条记录")
            print("\n最近5条财务记录:")
            # 只显示关键列
            key_columns = ["statDate", "roeAvg", "epsTTM", "netProfit"]
            available_columns = [col for col in key_columns if col in financial_df.columns]
            if available_columns:
                print(financial_df[available_columns].tail().to_string(index=False))
            else:
                print(financial_df.tail().to_string(index=False))
        else:
            print("⚠️  未获取到财务数据")

        # 5. 显示缓存统计
        print(f"\n📦 5. 缓存统计")
        print("-" * 40)
        stats = client.get_cache_stats()
        print(f"命中次数: {stats['hits']}")
        print(f"未命中次数: {stats['misses']}")
        print(f"命中率: {stats['hit_rate'] * 100:.1f}%")
        print(f"缓存大小: {stats['cache_size']} 条")

    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()
        print("\n✅ 完成")


if __name__ == "__main__":
    main()
