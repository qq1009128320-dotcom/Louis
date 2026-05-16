"""财务数据 akshare 实现"""
import akshare as ak
import pandas as pd


def get_akshare_metrics(symbol):
    """从 akshare 获取关键财务指标"""
    metrics = {}
    
    try:
        # 财务分析指标 (含ROE/ROA等)
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df is not None and not df.empty:
            # 取最新一期
            latest = df.iloc[-1]
            
            _safe_get(metrics, latest, "净资产收益率(%)", "roe", "ROE(%)")
            _safe_get(metrics, latest, "总资产报酬率(%)", "roa", "ROA(%)")
            _safe_get(metrics, latest, "销售毛利率(%)", "gross_profit_margin", "毛利率(%)")
            _safe_get(metrics, latest, "销售净利率(%)", "net_profit_margin", "净利率(%)")
            _safe_get(metrics, latest, "营业利润率(%)", "operating_profit_margin", "营业利润率(%)")
            _safe_get(metrics, latest, "营业总收入增长率(%)", "revenue_growth", "营收增长率(%)")
            _safe_get(metrics, latest, "归属母公司净利润增长率(%)", "profit_growth", "净利润增长率(%)")
            _safe_get(metrics, latest, "资产负债率(%)", "debt_ratio", "资产负债率(%)")
            _safe_get(metrics, latest, "流动比率", "current_ratio", "流动比率")
            _safe_get(metrics, latest, "速动比率", "quick_ratio", "速动比率")
    except Exception as e:
        metrics["_analysis_error"] = str(e)[:100]
    
    try:
        # 利润表 - 最新年度的每股收益等
        df2 = ak.stock_profit_sheet_by_yearly_em(symbol=_em_code(symbol))
        if df2 is not None and not df2.empty:
            latest2 = df2.iloc[-1]
            _safe_get(metrics, latest2, "基本每股收益", "eps", "每股收益")
    except:
        pass
    
    return metrics


def _em_code(symbol):
    """转换为东方财富格式: 600036 → SH600036"""
    symbol = str(symbol).strip().upper()
    if symbol.startswith(("SH", "SZ")):
        return symbol
    prefix = "SH" if symbol.startswith(("6", "9")) else "SZ"
    return f"{prefix}{symbol}"


def _safe_get(metrics, row, col, metric_key=None, display_key=None):
    """安全取值"""
    key = display_key or metric_key or col
    try:
        val = row.get(col)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            metrics[key] = f"{float(val):.2f}" if isinstance(val, (int, float)) else str(val)
    except:
        pass
