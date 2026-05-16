"""基础数据层：财务摘要 + 资产负债表 + 利润表 + 现金流量 (akshare + mootdx 双源)"""
from datetime import datetime


class FinancialData:
    """财务数据查询"""
    
    def get_key_metrics(self, symbol):
        """获取关键财务指标"""
        metrics = {}
        
        # 方案1: akshare 财务分析指标
        try:
            from layers.finance_akshare import get_akshare_metrics
            metrics.update(get_akshare_metrics(symbol))
        except Exception as e:
            metrics["error_akshare"] = str(e)
        
        # 方案2: mootdx 财务数据
        # try:
        #     from layers.finance_mootdx import get_mootdx_metrics
        #     metrics.update(get_mootdx_metrics(symbol))
        # except:
        #     pass
        
        return metrics
    
    def print_metrics(self, metrics):
        if not metrics or "error_akshare" in metrics and len(metrics) == 1:
            print(f"  财务数据获取失败: {metrics.get('error_akshare', '未知错误')}")
            return
        
        print(f"\n{'='*75}")
        print(f"  财务关键指标")
        print(f"{'='*75}")
        
        # 估值指标
        val_keys = ["市盈率", "市净率", "市销率", "总市值(亿)", "流通市值(亿)"]
        print(f"\n  ── 估值指标 ──")
        for k in val_keys:
            if k in metrics:
                print(f"  {k:<16} {metrics[k]}")
        
        # 盈利能力
        profit_keys = ["ROE(%)", "ROA(%)", "毛利率(%)", "净利率(%)", "营业利润率(%)"]
        print(f"\n  ── 盈利能力 ──")
        for k in profit_keys:
            if k in metrics:
                print(f"  {k:<16} {metrics[k]}")
        
        # 成长性
        growth_keys = ["营收增长率(%)", "净利润增长率(%)", "扣非净利润增长率(%)"]
        print(f"\n  ── 成长性 ──")
        for k in growth_keys:
            if k in metrics:
                print(f"  {k:<16} {metrics[k]}")
        
        # 财务健康
        health_keys = ["资产负债率(%)", "流动比率", "速动比率", "权益乘数"]
        print(f"\n  ── 财务健康 ──")
        for k in health_keys:
            if k in metrics:
                print(f"  {k:<16} {metrics[k]}")
        
        # 每股指标
        eps_keys = ["每股收益", "每股净资产", "每股现金流", "每股股息"]
        print(f"\n  ── 每股指标 ──")
        for k in eps_keys:
            if k in metrics:
                print(f"  {k:<16} {metrics[k]}")
        
        print(f"\n{'='*75}\n")
