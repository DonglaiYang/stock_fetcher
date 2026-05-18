# stock_fetcher

A股股票数据获取工具。获取所有 A 股的周度行情数据、基本面数据和近期新闻，可用于 LLM 训练数据集构建。

## 项目结构

```
stock_fetcher/
├── main.py                 # 主程序入口
├── utils/
│   ├── __init__.py
│   ├── symbols_fetcher.py  # 获取 A 股股票列表
│   ├── news_fetcher.py     # 获取股票新闻
│   └── check.py            # 数据完整性检查
├── data/
│   ├── A_stock_list.csv    # 股票代码列表
│   └── stock_info/         # 含所有股票的周度数据(CSV)以及一个汇总后的新闻数据文件（CSV）
└── requirements.txt
```

## 使用方法

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行主程序（若要重新生成data文件则去掉get_symbol_info()、get_news_info()的注释，否则就只检擦数据完整性）：

```bash
python main.py
```

## 数据说明

每只股票的 CSV 文件包含以下字段：

| 字段 | 说明 |
|------|------|
| 数据可用 | 该股票在时间范围内是否有交易数据 |
| 公司信息 | 公司基本信息（行业、上市时间、市值等） |
| 基本面 | 季度财务数据（净利润增长率、资产负债率等） |
| 起始日期 | 本周起始日期（周一） |
| 结算日期 | 本周结算日期（周五） |
| 起始价 | 本周开盘价 |
| 结算价 | 本周收盘价 |
| 周收益率 | 本周收益率 |
| 涨跌标签 | 涨跌幅分类标签（涨1至涨5+、跌1至跌5+、平） |


## 日期配置

在 `main.py` 中修改以下变量：

- `START_DATE`：数据起始日期
- `END_DATE`：数据结束日期
