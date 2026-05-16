"""
财务数据 akshare 实现 v1.2
修复: 使用英文/数字列名匹配（akshare 实际返回的列名）
"""
import logging
import pandas as pd

logger = logging.getLogger("a-share-finance")

# akshare stock_financial_analysis_indicator 实际列名映射
# 格式: (akshare列名, 显示名)
COLUMN_MAP = [
    ("净资产收益率(%)", "ROE(%)"),
    ("净资产收益率", "ROE(%)"),
    ("总资产报酬率(%)", "ROA(%)"),
    ("总资产报酬率", "ROA(%)"),
    ("销售毛利率(%)", "毛利率(%)"),
    ("销售毛利率", "毛利率(%)"),
    ("销售净利率(%)", "净利率(%)"),
    ("销售净利率", "净利率(%)"),
    ("营业利润率(%)", "营业利润率(%)"),
    ("营业利润率", "营业利润率(%)"),
    ("营业总收入增长率(%)", "营收增长率(%)"),
    ("营业总收入增长率", "营收增长率(%)"),
    ("归属母公司净利润增长率(%)", "净利润增长率(%)"),
    ("归属母公司净利润增长率", "净利润增长率(%)"),
    ("资产负债率(%)", "资产负债率(%)"),
    ("资产负债率", "资产负债率(%)"),
    ("流动比率", "流动比率"),
    ("速动比率", "速动比率"),
]


def get_akshare_metrics(symbol):
    """从 akshare 获取关键财务指标"""
    metrics = {}

    try:
        import akshare as ak
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df is not None and not df.empty:
            latest = df.iloc[-1]

            # 用映射表逐个尝试中英文列名
            for akshare_col, display_name in COLUMN_MAP:
                val = _safe_get_val(latest, akshare_col)
                if val is not None:
                    metrics[display_name] = f"{val:.2f}"
    except ImportError:
        logger.debug("财务指标: akshare not available")
    except Exception as e:
        logger.warning(f"财务指标({symbol}): {type(e).__name__}: {e}")
        metrics["_analysis_error"] = str(e)[:100]

    # 利润表 - 每股收益
    try:
        import akshare as ak
        df2 = ak.stock_profit_sheet_by_yearly_em(symbol=_em_code(symbol))
        if df2 is not None and not df2.empty:
            latest2 = df2.iloc[-1]
            eps = _safe_get_val(latest2, "基本每股收益")
            if eps is not None:
                metrics["每股收益"] = f"{eps:.2f}"
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"每股收益({symbol}): {type(e).__name__}")

    return metrics


def _em_code(symbol):
    """转换为东方财富格式: 600036 → SH600036"""
    symbol = str(symbol).strip().upper()
    if symbol.startswith(("SH", "SZ")):
        return symbol
    prefix = "SH" if symbol.startswith(("6", "9")) else "SZ"
    return f"{prefix}{symbol}"


def _safe_get_val(row, col):
    """从 DataFrame 行安全取值，返回 float 或 None"""
    try:
        val = row.get(col)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            return float(val)
    except (ValueError, TypeError):
        pass
    return None
