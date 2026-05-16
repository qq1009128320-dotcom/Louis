#!/usr/bin/env python3
"""
A股全维度数据系统 - 统一入口
=================================
六层数据架构：

  行情层  →  mootdx + 腾讯财经      实时行情、K线
  研报层  →  akshare 东方财富       机构研报、评级、盈利预测
  信号层  →  akshare 东方财富       板块资金流、概念热点、个股资金
  新闻层  →  akshare x3            财联社电报、东方财富个股新闻、同花顺综合
  基础数据 →  mootdx + akshare      财务摘要、资产负债表、利润表、现金流量
  公告层  →  akshare 巨潮          定期报告披露、公告查询

用法:
  python3 a_stock.py quote 600036 000858        # 行情
  python3 a_stock.py kline 600036 -p day -c 20  # K线
  python3 a_stock.py research 600036            # 研报
  python3 a_stock.py signal                     # 信号(资金流+热点)
  python3 a_stock.py news                       # 新闻
  python3 a_stock.py finance 600036             # 财务
  python3 a_stock.py announce 600036            # 公告
  python3 a_stock.py monitor 600036 000858      # 监控
"""

import argparse
import sys
import os
import time
from datetime import datetime

# 把当前目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layers.quotes import TencentQuotes, MootdxQuotes
from layers.research import ResearchReports
from layers.signal import SignalScanner
from layers.news import NewsFeed
from layers.finance import FinancialData
from layers.announce import Announcements


def cmd_quote(args):
    """行情查询"""
    try:
        q = TencentQuotes()
    except:
        q = MootdxQuotes()
    
    data = q.get_quotes(args.symbols)
    q.print_table(data)


def cmd_kline(args):
    """K线查询"""
    try:
        q = TencentQuotes()
    except:
        q = MootdxQuotes()
    
    data = q.get_kline(args.symbols, period=args.period, count=args.count)
    q.print_kline(data, args.period)


def cmd_research(args):
    """研报查询"""
    r = ResearchReports()
    data = r.get_reports(args.symbol)
    r.print_reports(data)


def cmd_signal(args):
    """信号扫描"""
    s = SignalScanner()
    results = s.scan()
    s.print_results(results)


def cmd_news(args):
    """新闻查询"""
    n = NewsFeed()
    data = n.get_news(args.symbol)
    n.print_news(data)


def cmd_finance(args):
    """财务数据"""
    f = FinancialData()
    key_metrics = f.get_key_metrics(args.symbol)
    f.print_metrics(key_metrics)


def cmd_announce(args):
    """公告查询"""
    a = Announcements()
    data = a.get_announcements(args.symbol, args.start, args.end)
    a.print_announcements(data)


def cmd_monitor(args):
    """实时监控"""
    try:
        q = TencentQuotes()
    except:
        q = MootdxQuotes()
    
    print(f"\n  A股实时监控 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 间隔 {args.interval}s")
    print(f"  标的: {', '.join(args.symbols)}")
    print(f"  {'代码':<8} {'现价':>8} {'涨幅':>8} {'最高':>8} {'最低':>8}")
    
    while True:
        try:
            data = q.get_quotes(args.symbols)
            for item in data:
                chg = item.get('change_pct', 0) or 0
                try:
                    chg = float(chg)
                except:
                    chg = 0
                print(f"  {item['code']:<8} {item['price']:>8} {chg:>+7.2f}% {item.get('high','-'):>8} {item.get('low','-'):>8}")
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n  监控停止")
            break
        except Exception as e:
            print(f"  [错误] {e}")
            time.sleep(args.interval)


def main():
    parser = argparse.ArgumentParser(description="A股全维度数据系统 v1.0")
    sub = parser.add_subparsers(dest="command", help="数据层")
    
    # 行情
    p_quote = sub.add_parser("quote", help="实时行情")
    p_quote.add_argument("symbols", nargs="+", help="股票代码")
    p_quote.set_defaults(func=cmd_quote)
    
    # K线
    p_kline = sub.add_parser("kline", help="K线数据")
    p_kline.add_argument("symbols", nargs="+", help="股票代码")
    p_kline.add_argument("-p", "--period", default="day",
                         help="周期: day/week/month/min5/min15/min30/min60")
    p_kline.add_argument("-c", "--count", type=int, default=20, help="条数")
    p_kline.set_defaults(func=cmd_kline)
    
    # 研报
    p_res = sub.add_parser("research", help="机构研报")
    p_res.add_argument("symbol", help="股票代码")
    p_res.set_defaults(func=cmd_research)
    
    # 信号
    p_sig = sub.add_parser("signal", help="信号扫描(资金流+热点)")
    p_sig.set_defaults(func=cmd_signal)
    
    # 新闻
    p_news = sub.add_parser("news", help="财经新闻")
    p_news.add_argument("symbol", nargs="?", help="股票代码(可选，留空看全局)")
    p_news.set_defaults(func=cmd_news)
    
    # 财务
    p_fin = sub.add_parser("finance", help="财务数据")
    p_fin.add_argument("symbol", help="股票代码")
    p_fin.set_defaults(func=cmd_finance)
    
    # 公告
    p_ann = sub.add_parser("announce", help="公告查询")
    p_ann.add_argument("symbol", help="股票代码")
    p_ann.add_argument("-s", "--start", default=None, help="开始日期 YYYYMMDD")
    p_ann.add_argument("-e", "--end", default=None, help="结束日期 YYYYMMDD")
    p_ann.set_defaults(func=cmd_announce)
    
    # 监控
    p_mon = sub.add_parser("monitor", help="实时监控")
    p_mon.add_argument("symbols", nargs="+", help="股票代码")
    p_mon.add_argument("-i", "--interval", type=int, default=5, help="刷新间隔(秒)")
    p_mon.set_defaults(func=cmd_monitor)
    
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
