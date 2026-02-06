#!/usr/bin/env python3
"""
查找高股息标的

使用真实数据计算并筛选当前市场上股息率较高的优质标的。
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finagent.data.client import DataClient, DataClientConfig


def main():
    # 创建数据客户端
    config = DataClientConfig(
        provider='baostock',
        enable_cache=True,
        rate_limit=1.0,
    )
    client = DataClient(config)

    print('正在获取股票列表...')
    stocks_df = client.get_stocks_list()
    print(f'获取到 {len(stocks_df)} 只股票')

    # 获取一些知名的蓝筹股进行分析
    blue_chips = [
        'sh.600036',  # 招商银行
        'sh.600000',  # 浦发银行
        'sh.601398',  # 工商银行
        'sh.601939',  # 建设银行
        'sh.601318',  # 中国平安
        'sh.600519',  # 贵州茅台
        'sz.000001',  # 平安银行
        'sz.000002',  # 万科A
        'sz.000333',  # 美的集团
        'sz.000858',  # 五粮液
        'sh.600276',  # 恒瑞医药
        'sh.600887',  # 伊利股份
        'sh.601288',  # 农业银行
        'sh.601166',  # 兴业银行
        'sh.600016',  # 民生银行
        'sz.000651',  # 格力电器
        'sz.002415',  # 海康威视
        'sh.601888',  # 中国中车
        'sh.600028',  # 中国石化
        'sh.601857',  # 中国石油
    ]

    print(f'\n分析 {len(blue_chips)} 只蓝筹股的股息率...')

    # 获取最新价格
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

    results = []
    for code in blue_chips:
        try:
            stock_info = client.get_stock_info(code)
            history_df = client.get_history_data(code, start_date, end_date, 'd')
            if not history_df.empty:
                latest_price = history_df.iloc[-1]['close']

                # 获取分红数据
                dividend_df = client.get_dividend_data(code)
                if not dividend_df.empty and len(dividend_df) >= 2:
                    recent_dividends = dividend_df.tail(3)
                    avg_dividend = recent_dividends['dividendOperateRatio'].mean() / 10  # 转换为每股分红

                    # 计算股息率
                    dividend_yield = (avg_dividend / latest_price) * 100

                    results.append({
                        'code': code,
                        'name': stock_info.name,
                        'price': latest_price,
                        'avg_dividend': avg_dividend,
                        'dividend_yield': dividend_yield
                    })
        except Exception as e:
            print(f'{code}: {e}')

    # 按股息率排序
    results.sort(key=lambda x: x['dividend_yield'], reverse=True)

    print('\n=== 高股息蓝筹股排名 ===')
    header = f"{'股票代码':<12} {'股票名称':<12} {'当前价':<10} {'每股分红':<12} {'股息率':<10}"
    print(header)
    print('-' * 60)
    for r in results[:15]:
        print(f"{r['code']:<12} {r['name']:<12} {r['price']:>8.2f}   {r['avg_dividend']:>8.3f}   {r['dividend_yield']:>6.2f}%")

    # 显示缓存统计
    stats = client.get_cache_stats()
    print(f'\n缓存统计: 命中率 {stats["hit_rate"]*100:.1f}%')

    client.close()
    print('\n分析完成！')


if __name__ == "__main__":
    main()
