# a-share-analyst

A股全维度数据系统 — 六层架构

## 架构

- 行情层：腾讯财经 qt.gtimg.cn + mootdx 备用
- 研报层：akshare → 东方财富 reportapi
- 信号层：akshare → 东方财富 fund flow
- 新闻层：akshare ×3 源聚合（财联社/东方财富/同花顺）
- 基础数据层：akshare 财务分析（ROE/PE/PB/增长率）
- 公告层：akshare → 巨潮资讯 cninfo

## 用法

```bash
cd skills/a-share-analyst
python3 a_stock.py quote 600036 000858 300750 sh000001
python3 a_stock.py kline 600036 -p day -c 20
python3 a_stock.py research 600036
python3 a_stock.py signal
python3 a_stock.py news
python3 a_stock.py finance 600036
```

## 依赖

Python 3.8+, akshare, (可选)mootdx
