"""公告层：巨潮资讯网 + mootdx 公告 (akshare) v1.2"""
from datetime import datetime, timedelta
import logging
logger = logging.getLogger("a-share-announce")


class Announcements:
    """上市公司公告查询"""
    
    def get_announcements(self, symbol, start=None, end=None):
        """
        获取公告列表
        symbol: 股票代码
        start/end: YYYYMMDD 格式日期，默认最近30天
        """
        if not end:
            end = datetime.now().strftime("%Y%m%d")
        if not start:
            start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        results = []
        
        # 方案1: akshare 巨潮
        try:
            import akshare as ak
            df = ak.stock_zh_a_disclosure_report_cninfo(
                symbol=symbol, market="沪深京",
                start_date=start, end_date=end
            )
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    results.append({
                        "title": str(row.get("title", row.get("公告标题", ""))),
                        "date": str(row.get("date", row.get("公告日期", ""))),
                        "type": str(row.get("type", row.get("公告类型", ""))),
                        "source": "巨潮资讯",
                        "url": str(row.get("url", row.get("公告链接", ""))),
                    })
        except ImportError:
            pass
        except Exception as e:
            pass
        
        # 方案2: mootdx affair (财务文件)
        try:
            from mootdx.affair import Affair
            files = Affair.files()
            if files:
                for f in files[:10]:
                    results.append({
                        "title": f.get("filename", ""),
                        "date": f.get("date", ""),
                        "type": "财务文件",
                        "source": "通达信",
                        "url": "",
                    })
        except:
            pass
        
        return sorted(results, key=lambda x: x.get("date", ""), reverse=True)[:20]
    
    def print_announcements(self, announcements):
        if not announcements:
            print("  无公告数据")
            return
        
        print(f"\n{'='*85}")
        print(f"  上市公司公告 (最近{len(announcements)}条)")
        print(f"{'='*85}")
        
        for i, a in enumerate(announcements):
            print(f"\n  [{a.get('source', '')}] {a.get('date', '')[:10]}")
            print(f"  {a.get('title', '')[:80]}")
            if a.get('url'):
                print(f"  🔗 {a['url']}")
        
        print(f"\n{'='*85}\n")
