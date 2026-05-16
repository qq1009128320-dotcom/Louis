"""研报层：东方财富机构研报 (akshare) v1.2"""
from datetime import datetime
import logging
logger = logging.getLogger("a-share-research")


class ResearchReports:
    """机构研报查询"""
    
    def get_reports(self, symbol, count=10):
        """获取个股研报"""
        try:
            import akshare as ak
            df = ak.stock_research_report_em(symbol=symbol)
            if df is None or df.empty:
                return []
            
            # 按日期倒序，取最近N条
            if "infoDate" in df.columns:
                df = df.sort_values("infoDate", ascending=False)
            
            reports = []
            for _, row in df.head(count).iterrows():
                reports.append({
                    "title": str(row.get("researchTitle", row.get("title", ""))),
                    "org": str(row.get("orgSName", row.get("orgName", ""))),
                    "rate": str(row.get("rate", row.get("rating", ""))),
                    "date": str(row.get("infoDate", row.get("date", ""))),
                    "author": str(row.get("author", "")),
                    "change": str(row.get("change", row.get("profitChange", ""))),
                    "target_price": str(row.get("targetPrice", "")),
                })
            return reports
        except ImportError:
            logger.debug("研报: akshare not available")
            return []
        except Exception as e:
            logger.warning(f"研报({symbol}): {type(e).__name__}: {e}")
            return []
    
    def print_reports(self, reports):
        if not reports:
            print("  无研报数据")
            return
        
        print(f"\n{'='*80}")
        print(f"  机构研报 (最近{len(reports)}篇)")
        print(f"{'='*80}")
        for r in reports:
            date = r.get("date", "")[:10]
            org = r.get("org", "未知机构")
            rate = r.get("rate", "-")
            title = r.get("title", "")
            author = r.get("author", "")
            change = r.get("change", "")
            target = r.get("target_price", "")
            
            print(f"\n  [{date}] {org} | 评级: {rate}")
            print(f"  {title[:80]}")
            extra = []
            if author:
                extra.append(f"作者: {author}")
            if change:
                extra.append(f"盈利变化: {change}")
            if target:
                extra.append(f"目标价: {target}")
            if extra:
                print(f"  {' | '.join(extra)}")
        print(f"\n{'='*80}\n")
