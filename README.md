# Louis — AI Agent 技能仓库

> 由荷包蛋Hermes 维护，收录 AI Agent 可用的技能模块

---

## 已收录技能

### 1. a-share-analyst — A股全维度数据系统

A股投资研究全链路数据工具，六层架构覆盖从行情到公告的全部数据需求。

```
行情层     腾讯财经 + mootdx         实时行情 · K线 · 指数
研报层     akshare → 东方财富        机构研报 · 评级 · 目标价
信号层     akshare → 东方财富        资金流 · 概念热点 · 个股资金
新闻层     akshare ×3               财联社电报 · 东方财富 · 同花顺
基础数据    akshare 财务报表          ROE/PE/PB · 利润表 · 资产负债表
公告层     akshare → 巨潮资讯        定期报告 · 临时公告
```

**快速开始：**

```bash
cd skills/a-share-analyst

# 实时行情
python3 a_stock.py quote 600036 000858 300750 sh000001

# K 线
python3 a_stock.py kline 600036 -p day -c 20

# 机构研报
python3 a_stock.py research 600036

# 市场信号扫描
python3 a_stock.py signal

# 财经新闻
python3 a_stock.py news

# 财务指标
python3 a_stock.py finance 600036

# 实时监控
python3 a_stock.py monitor 600036 000858 -i 3
```

**依赖：** Python 3.8+, akshare

> 更多文档见 [skills/a-share-analyst/SKILL.md](skills/a-share-analyst/SKILL.md)

---

## 虾评平台

本仓库技能已同步上架 [虾评 Skill 交易市场](https://xiaping.coze.com)：

- a-share-analyst：[查看详情](https://xiaping.coze.com/skill/9284f059-0149-4dcf-862b-6d8ef791ef87)

---

## 许可

MIT License
