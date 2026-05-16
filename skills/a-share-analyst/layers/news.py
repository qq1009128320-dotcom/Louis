"""新闻层：财联社 + 东方财富 + 同花顺 三方聚合 (akshare)"""
from datetime import datetime


class NewsFeed:
    """聚合财经新闻，三源归一"""
    
    def get_news(self, symbol=None, limit=15):
        """
        获取新闻。symbol 为空 → 全局要闻，非空 → 个股新闻
        三源：财联社(快讯)、东方财富(个股)、同花顺(综合)
        """
        results = []
        
        if symbol:
            results.extend(self._eastmoney_stock_news(symbol, limit))
        else:
            results.extend(self._cls_news(limit))
            results.extend(self._ths_news(limit))
        
        # 去重+排序
        return sorted(results, key=lambda x: x.get("time", ""), reverse=True)[:limit]
    
    def _cls_news(self, limit=10):
        """财联社电报 — 实时快讯"""
        try:
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
        except:
            return []
    
    def _eastmoney_stock_news(self, symbol, limit=10):
        """东方财富个股新闻"""
        try:
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
        except:
            return []
    
    def _ths_news(self, limit=10):
        """同花顺综合资讯"""
        try:
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
        except:
            return []
    
    def print_news(self, news_list):
        if not news_list:
            print("  无新闻数据")
            return
        
        print(f"\n{'='*85}")
        print(f"  财经新闻聚合 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
