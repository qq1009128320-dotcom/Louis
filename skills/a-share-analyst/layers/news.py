"""
新闻层：财联社 + 东方财富 + 同花顺 三方聚合 (akshare)
v1.2: 修复个股新闻缺源、去重逻辑、加错误日志
"""
from datetime import datetime
import logging

logger = logging.getLogger("a-share-news")


class NewsFeed:
    """聚合财经新闻，三源归一"""

    def get_news(self, symbol=None, limit=15):
        """
        symbol 为空 → 全局要闻（财联社+同花顺）
        symbol 非空 → 三源聚合：东方财富个股新闻 + 财联社 + 同花顺
        """
        results = []

        # 全局要闻
        if not symbol:
            results.extend(self._fetch("财联社", self._cls_news, limit))
            results.extend(self._fetch("同花顺", self._ths_news, limit))
        else:
            # 个股：三源都查
            results.extend(self._fetch("东方财富", self._eastmoney_stock_news, symbol, limit))
            results.extend(self._fetch("财联社", self._cls_news, limit))
            results.extend(self._fetch("同花顺", self._ths_news, limit))

        # 去重：按标题前30字去重
        seen = set()
        deduped = []
        for n in sorted(results, key=lambda x: x.get("time", ""), reverse=True):
            key = n.get("title", "")[:30]
            if key and key not in seen:
                seen.add(key)
                deduped.append(n)

        return deduped[:limit]

    def _fetch(self, source, func, *args, **kwargs):
        """带错误日志的统一抓取"""
        try:
            return func(*args, **kwargs)
        except ImportError:
            logger.debug(f"{source}: akshare not available")
            return []
        except Exception as e:
            logger.warning(f"{source}: {type(e).__name__}: {e}")
            return []

    def _cls_news(self, limit=10):
        """财联社电报 — 实时快讯"""
        import akshare as ak
        df = ak.stock_info_global_cls()
        if df is None or df.empty:
            return []

        news = []
        for _, row in df.head(limit).iterrows():
            news.append({
                "source": "财联社",
                "title": str(row.get("title", row.get("标题", ""))),
                "content": str(row.get("content", row.get("内容", "")))[:200],
                "time": str(row.get("time", row.get("时间", ""))),
            })
        return news

    def _eastmoney_stock_news(self, symbol, limit=10):
        """东方财富个股新闻"""
        import akshare as ak
        df = ak.stock_news_em(symbol=symbol)
        if df is None or df.empty:
            return []

        news = []
        for _, row in df.head(limit).iterrows():
            news.append({
                "source": "东方财富",
                "title": str(row.get("title", "")),
                "content": str(row.get("content", ""))[:200],
                "time": str(row.get("date", "")),
            })
        return news

    def _ths_news(self, limit=10):
        """同花顺综合资讯"""
        import akshare as ak
        df = ak.stock_info_global_ths()
        if df is None or df.empty:
            return []

        news = []
        for _, row in df.head(limit).iterrows():
            news.append({
                "source": "同花顺",
                "title": str(row.get("title", "")),
                "content": str(row.get("content", ""))[:200],
                "time": str(row.get("time", "")),
            })
        return news

    def print_news(self, news_list):
        if not news_list:
            print("  无新闻数据")
            return

        print(f"\n{'='*85}")
        print(f"  财经新闻聚合 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  {len(news_list)}条")
        print(f"{'='*85}")

        for i, n in enumerate(news_list):
            source = n.get("source", "")
            title = n.get("title", "")
            time_str = n.get("time", "")
            content = n.get("content", "")

            print(f"\n  [{source}] {title[:80]}")
            if time_str:
                print(f"  ⏰ {time_str}")
            if content:
                print(f"  {content[:150]}")

        print(f"\n{'='*85}\n")
