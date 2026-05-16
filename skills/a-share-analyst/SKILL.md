---
name: a-share-analyst
description: A股全维度数据系统 — 六层架构：行情(腾讯+mootdx)、研报(东方财富)、信号(资金流+热点)、新闻(财联社/东财/同花顺)、财务(akshare)、公告(巨潮)
version: 1.1.0
author: hermes
license: MIT
platforms: [linux]
metadata:
  hermes:
    triggers: [A股, 股票数据, 行情, 研报, 资金流, 财务, 公告, a_stock, a-share-analyst]
---

# A股全维度数据系统 (a-share-analyst)

六层数据架构，覆盖 A 股投资研究全链路。

## 系统架构

```
┌─────────────────────────────────────────────┐
│              行情层 (Quotes)                 │
│  腾讯财经 qt.gtimg.cn   +   mootdx 备用      │
│  实时行情 · K线(日/周/月/分钟) · 指数        │
├─────────────────────────────────────────────┤
│              研报层 (Research)               │
│  akshare → 东方财富 reportapi               │
│  机构研报 · 评级 · 盈利预测 · 目标价         │
├─────────────────────────────────────────────┤
│              信号层 (Signal)                 │
│  akshare → 东方财富 fund flow               │
│  行业资金流 · 概念热点 · 个股资金            │
├─────────────────────────────────────────────┤
│              新闻层 (News)                   │
│  akshare ×3 源聚合                          │
│  财联社电报 · 东方财富个股 · 同花顺综合      │
├─────────────────────────────────────────────┤
│            基础数据层 (Finance)              │
│  akshare 财务分析 + 三大报表                 │
│  ROE/ROA/毛利率/PE/PB · 利润表 · 资产负债表  │
├─────────────────────────────────────────────┤
│              公告层 (Announce)               │
│  akshare → 巨潮资讯 cninfo                  │
│  定期报告 · 临时公告 · 财务文件               │
└─────────────────────────────────────────────┘
```

## 入口

路径: `/home/administrator/tools/a-share-analyst/a_stock.py`

```bash
cd /home/administrator/tools/a-share-analyst

# 实时行情
python3 a_stock.py quote 600036 000858 300750 sh000001

# K线
python3 a_stock.py kline 600036 -p day -c 20
python3 a_stock.py kline 600036 -p week -c 50

# 研报
python3 a_stock.py research 600036

# 信号扫描
python3 a_stock.py signal

# 新闻（全局）
python3 a_stock.py news
# 新闻（个股）
python3 a_stock.py news 600036

# 财务指标
python3 a_stock.py finance 600036

# 公告
python3 a_stock.py announce 600036

# 实时监控
python3 a_stock.py monitor 600036 000858 -i 3
```

## 股票代码规则

- `600036` → 自动映射 sh (上海)
- `000858` → 自动映射 sz (深圳)
- `sh000001` → 显式指定 上证指数
- `sz399001` → 显式指定 深证成指

## 依赖

- **必需**: Python 3.8+, akshare
- **可选**: mootdx (行情备用引擎，无 mootdx 时仅用腾讯)

## 层模块结构

```
/home/administrator/tools/a-share-analyst/
├── a_stock.py              # 统一入口 CLI
└── layers/
    ├── quotes.py           # 行情层 (Tencent + Mootdx)
    ├── research.py         # 研报层 (东方财富)
    ├── signal.py           # 信号层 (资金流+概念)
    ├── news.py             # 新闻层 (三源聚合)
    ├── finance.py          # 基础数据层 (入口)
    ├── finance_akshare.py  # 财务 akshare 实现
    └── announce.py         # 公告层 (巨潮)
```

## 数据源可靠性

| 层 | 主源 | 备用 | 可靠性 |
|----|------|------|--------|
| 行情 | 腾讯 qt.gtimg.cn | mootdx | ⭐⭐⭐⭐⭐ 极高 |
| 研报 | akshare→东方财富 | - | ⭐⭐⭐⭐ 高 |
| 信号 | akshare→东方财富 | - | ⭐⭐⭐ 中(偶有连接中断) |
| 新闻 | akshare×3 | - | ⭐⭐⭐⭐ 高 |
| 财务 | akshare→东方财富 | - | ⭐⭐⭐⭐ 高 |
| 公告 | akshare→巨潮 | mootdx | ⭐⭐⭐ 中 |

## 注意事项

1. akshare 函数签名可能随版本变化，遇到报错先检查函数签名
2. 东方财富 API 在 WSL 下偶有 RemoteDisconnected 错误，属于网络波动
3. 上证指数请用 `sh000001`，不要用 `000001`（那是平安银行）
4. 行情层优先用腾讯财经，mootdx 仅作降级备用
5. 收盘后（15:00-次日9:30）行情数据为当日收盘价
6. 腾讯K线返回列数可能为6或7，`market_data.py` 已做容错（取前6列）

## 下游集成

本 skill 为焚诀交易引擎 v4.0 的数据源：

```
/home/administrator/.hermes/hermes-agent/stock_trader/
├── market_data.py   ← 适配层，封装 a-share-analyst 为引擎接口
├── scanner.py       ← 全市场扫描器（行业热度→初筛→四维深评）
└── engine.py        ← 四维评分引擎（技术35+资金25+财务20+情绪20）
```

引擎定时任务：
- 早盘扫描：周一~五 9:35（hermes cron `早盘扫描`）
- 收盘日报：周一~五 15:30（hermes cron `收盘日报`）

## WSL 实战记录

- akshare 东方财富资金流 API（`stock_sector_fund_flow_rank`、`stock_board_concept_spot_em`）在 WSL 下频繁 RemoteDisconnected，引擎评分中资金面会降为零分
- 财务数据 API（`stock_financial_analysis_indicator`）同样受影响
- **降级方案**：scanner.py 的 `_fallback_sector_ranking()` 用腾讯行情涨跌幅聚合来推断行业热度
- 行情层（腾讯 qt.gtimg.cn）和新闻层在 WSL 下稳定，不受影响

## 参考文档

- `references/mootdx-wsl-deployment.md` — mootdx 在 WSL 下的部署要点
- `references/skill-hub-submission.md` — 手动提交到 Hermes Skill Hub 的步骤
- `references/trading-engine-integration.md` — 与焚诀交易引擎 v4.0 的集成方式
