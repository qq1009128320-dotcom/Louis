"""
信号层：板块资金流 + 个股资金 + 概念热点 (akshare 东方财富)
v1.2: 扩展概念列表到20个 + 错误日志
"""
from datetime import datetime
import logging

logger = logging.getLogger("a-share-signal")

# 覆盖全市场主要概念板块
HOT_CONCEPTS = [
    "人工智能", "新能源车", "芯片", "机器人", "数字经济",
    "医药", "军工", "消费电子", "光伏", "储能",
    "半导体", "云计算", "大数据", "物联网", "元宇宙",
    "创新药", "锂电池", "风电", "氢能源", "信创",
]


class SignalScanner:
    """信号扫描器：资金流 + 热点概念"""

    def scan(self):
        results = {
            "sector_flow": self._safe("行业资金流", self._sector_fund_flow),
            "hot_concepts": self._safe("概念热点", self._hot_concepts),
        }
        return results

    def _safe(self, label, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ImportError:
            logger.debug(f"{label}: akshare not available")
            return []
        except Exception as e:
            logger.warning(f"{label}: {type(e).__name__}: {e}")
            return []

    def _sector_fund_flow(self):
        import akshare as ak
        df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
        if df is None or df.empty:
            return []

        sectors = []
        for _, row in df.iterrows():
            sectors.append({
                "name": str(row.get("名称", "")),
                "net_inflow": _safe_float(row.get("主力净流入-净额", 0)),
                "change_pct": _safe_float(row.get("涨跌幅", 0)),
                "net_ratio": _safe_float(row.get("主力净流入-净占比", 0)),
            })

        sectors.sort(key=lambda x: x["net_inflow"], reverse=True)
        return sectors[:10]

    def _hot_concepts(self):
        import akshare as ak
        concepts = []
        for name in HOT_CONCEPTS:
            try:
                df = ak.stock_board_concept_spot_em(symbol=name)
                if df is not None and not df.empty:
                    row = df.iloc[0]
                    chg = _safe_float(row.get("涨跌幅", 0))
                    if abs(chg) > 0.1:  # 过滤平盘概念
                        concepts.append({
                            "name": name,
                            "change_pct": chg,
                            "leader": str(row.get("名称", "")),
                            "leader_price": _safe_float(row.get("最新价", 0)),
                        })
            except Exception:
                pass  # 单个概念失败不影响其他

        concepts.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        return concepts[:10]

    def get_stock_fund_flow(self, symbol):
        try:
            import akshare as ak
            market = "sh" if symbol.startswith(("6", "9")) else "sz"
            df = ak.stock_individual_fund_flow(stock=symbol, market=market)
            if df is None or df.empty:
                return []

            flows = []
            for _, row in df.tail(10).iterrows():
                flows.append({
                    "date": str(row.get("日期", "")),
                    "close": _safe_float(row.get("收盘价", 0)),
                    "change_pct": _safe_float(row.get("涨跌幅", 0)),
                    "main_net": _safe_float(row.get("主力净流入-净额", 0)),
                    "main_ratio": _safe_float(row.get("主力净流入-净占比", 0)),
                    "super_large": _safe_float(row.get("超大单净流入-净额", 0)),
                    "large": _safe_float(row.get("大单净流入-净额", 0)),
                })
            return flows
        except ImportError:
            logger.debug("个股资金流: akshare not available")
            return []
        except Exception as e:
            logger.warning(f"个股资金流({symbol}): {type(e).__name__}: {e}")
            return []

    def print_results(self, results):
        print(f"\n{'='*85}")
        print(f"  市场信号扫描 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*85}")

        sf = results.get("sector_flow", [])
        if sf:
            print(f"\n  ── 行业资金流 TOP10 (主力净流入) ──")
            print(f"  {'行业':<16} {'净流入(亿)':>12} {'净占比':>8} {'涨跌幅':>8}")
            print("  " + "-" * 50)
            for s in sf[:10]:
                inflow = s["net_inflow"] / 1e8
                print(f"  {s['name']:<16} {inflow:>+11.2f}亿 {s['net_ratio']:>+7.2f}% {s['change_pct']:>+7.2f}%")

        hc = results.get("hot_concepts", [])
        if hc:
            print(f"\n  ── 热门概念板块 ──")
            print(f"  {'概念':<16} {'涨跌幅':>8} {'领涨股':<12} {'现价':>8}")
            print("  " + "-" * 50)
            for c in hc:
                print(f"  {c['name']:<16} {c['change_pct']:>+7.2f}% {c['leader']:<12} {c['leader_price']:>8.2f}")

        print(f"\n{'='*85}\n")


def _safe_float(v, default=0.0):
    try:
        return float(v) if v else default
    except (ValueError, TypeError):
        return default
