"""行情层：腾讯财经 + mootdx 双引擎"""
import json
import re
import urllib.request
from datetime import datetime


class TencentQuotes:
    """腾讯财经 qt.gtimg.cn — 零依赖，优先使用"""
    
    def _to_code(self, symbol):
        symbol = symbol.strip().upper()
        if symbol.startswith(("SH", "SZ", "BJ")):
            return symbol.lower()
        prefix = {"6": "sh", "9": "sh", "0": "sz", "3": "sz", "2": "sz"}.get(symbol[0], "sz")
        return f"{prefix}{symbol}"
    
    def get_quotes(self, symbols):
        codes = [self._to_code(s) for s in symbols]
        url = f"http://qt.gtimg.cn/q={','.join(codes)}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode("gbk", errors="replace")
        
        results = []
        for line in text.strip().split("\n"):
            if "=" not in line:
                continue
            parts = line.split("~")
            if len(parts) < 40:
                continue
            
            code = parts[2].strip()
            name = parts[1].strip()
            # 指数修正名称
            if not name or name == "0":
                name = {"000001": "上证指数", "399001": "深证成指",
                        "399006": "创业板指", "000688": "科创50"}.get(code, code)
            
            results.append({
                "code": code, "name": name,
                "price": parts[3], "last_close": parts[4], "open": parts[5],
                "high": parts[33], "low": parts[34],
                "change_pct": parts[32], "volume": parts[6],
                "amount": parts[37], "turnover": parts[38],
                "pe": parts[39], "pb": parts[46],
                "high_limit": parts[47], "low_limit": parts[48],
                "time": self._fmt_time(parts[30]) if len(parts) > 30 else "",
            })
        return results
    
    def _fmt_time(self, raw):
        if len(raw) == 14:
            return f"{raw[8:10]}:{raw[10:12]}:{raw[12:14]}"
        return raw
    
    def get_kline(self, symbols, period="day", count=100):
        freq_map = {"day": "day", "week": "week", "month": "month",
                    "min5": "m5", "min15": "m15", "min30": "m30", "min60": "m60"}
        freq = freq_map.get(period, "day")
        
        results = {}
        for sym in symbols:
            tc = self._to_code(sym)
            if period in ("day", "week", "month"):
                url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tc},{freq},,,{count},qfq"
                data_key = freq
            else:
                url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={tc},{freq},,{count}"
                data_key = freq
            
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            
            stock = data.get("data", {}).get(tc, {})
            klines = stock.get(data_key, []) or stock.get(f"qfq{data_key}", [])
            results[sym] = klines
        
        return results
    
    def print_table(self, data):
        print(f"\n{'='*85}")
        print(f"  A股实时行情 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*85}")
        print(f"{'代码':<8} {'名称':<10} {'现价':>10} {'涨跌幅':>8} {'开盘':>10} {'最高':>10} {'最低':>10} {'昨收':>10} {'成交量':>12}")
        print("-" * 85)
        for r in data:
            vol = r.get("volume", "0")
            try:
                vol = f"{int(vol):,}"
            except:
                pass
            print(f"{r['code']:<8} {r['name'][:10]:<10} {r['price']:>10} {r['change_pct']:>7}% "
                  f"{r['open']:>10} {r['high']:>10} {r['low']:>10} {r['last_close']:>10} {vol:>12}")
        print(f"{'='*85}\n")
    
    def print_kline(self, data, period):
        for sym, klines in data.items():
            if not klines:
                print(f"  {sym}: 无数据")
                continue
            print(f"\n  {sym} {period}K (最近{len(klines)}条)")
            print(f"  {'日期':<12} {'开盘':>8} {'收盘':>8} {'最高':>8} {'最低':>8} {'成交量':>12}")
            print("  " + "-" * 70)
            for k in klines[-20:]:
                if len(k) >= 6:
                    print(f"  {k[0]:<12} {k[1]:>8} {k[2]:>8} {k[3]:>8} {k[4]:>8} {k[5]:>12}")
            print()


class MootdxQuotes:
    """通达信 mootdx — 备选引擎"""
    
    def get_quotes(self, symbols):
        from mootdx.quotes import Quotes
        client = Quotes.factory(market="std")
        data = client.quotes(symbol=symbols)
        client.client.disconnect()
        
        if data is None or data.empty:
            return []
        
        results = []
        for _, row in data.iterrows():
            results.append({
                "code": str(row.get("code", "")),
                "name": str(row.get("name", "")),
                "price": str(row.get("price", "")),
                "last_close": str(row.get("last_close", "")),
                "open": str(row.get("open", "")),
                "high": str(row.get("high", "")),
                "low": str(row.get("low", "")),
                "change_pct": "",
                "volume": str(row.get("vol", "")),
                "amount": str(row.get("amount", "")),
                "turnover": "", "pe": "", "pb": "",
                "high_limit": "", "low_limit": "",
                "time": "",
            })
        return results
    
    def get_kline(self, symbols, period="day", count=100):
        from mootdx.quotes import Quotes
        freq_map = {"day": 9, "week": 5, "month": 6, "min15": 2,
                    "min30": 3, "min60": 4, "min5": 0}
        freq = freq_map.get(period, 9)
        
        client = Quotes.factory(market="std")
        results = {}
        for sym in symbols:
            bars = client.bars(symbol=sym, frequency=freq, offset=count)
            results[sym] = bars
        client.client.disconnect()
        return results
    
    def print_table(self, data):
        TencentQuotes().print_table(data)  # 复用打印
    
    def print_kline(self, data, period):
        TencentQuotes().print_kline(data, period)
