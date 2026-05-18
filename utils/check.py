import os
import json
import pandas as pd

def data_check():
    a_stock_path = "data/A_stock_list.csv"
    if os.path.exists(a_stock_path):
        df_list = pd.read_csv(a_stock_path, dtype = {"代码": str})
        print(f"\ndata/A_stock_list.csv 存在，共 {len(df_list)} 只股票\n")
    else:
        print(f"\ndata/A_stock_list.csv 不存在\n")


    all_news_path = "data/stock_info/all_news.csv"
    if os.path.exists(all_news_path):
        df_news = pd.read_csv(all_news_path, dtype = {"股票代码": str})
        print(f"data/stock_info/all_news.csv 存在，共 {len(df_news)} 条新闻")

        news_count = df_news.groupby("股票代码").size().reset_index(name = "新闻数量")
        has_news = len(news_count)

        df_list = pd.read_csv(a_stock_path, dtype = {"代码": str})
        all_symbols = set(df_list["代码"])
        no_news = all_symbols - set(df_news["股票代码"].unique())
        print(f"有新闻的股票: {has_news}")
        print(f"无新闻的股票: {len(no_news)}")

        print("新闻分布：")
        bins = [1, 3, 5, 10]
        prev = 1
        for b in bins:
            count = len(news_count[(news_count["新闻数量"] >= prev) & (news_count["新闻数量"] <= b)])
            if prev == b:
                print(f"正好 {b} 条: {count}")
            else:
                print(f"{prev}-{b} 条: {count}")
            prev = b + 1
        count = len(news_count[news_count["新闻数量"] > bins[-1]])
        print(f"{bins[-1]}+ 条: {count}\n")
    else:
        print(f"data/stock_info/all_news.csv 不存在\n")


    stock_info_path = "data/stock_info"
    if os.path.exists(stock_info_path):
        csv_files = [f for f in os.listdir(stock_info_path) if f.endswith(".csv")]
        print(f"data/stock_info 存在，共 {len(csv_files) - 1} 只股票")

        total_files = 0
        data_unavailable = 0
        basics_unavailable = 0
        normal_data = 0

        for f in csv_files:
            filepath = os.path.join(stock_info_path, f)
            df = pd.read_csv(filepath)

            if "数据可用" in df.columns:
                if not df["数据可用"].any():
                    data_unavailable += 1
                    continue
            else:
                data_unavailable += 1
                continue

            if "基本面" in df.columns:
                basics_column = df["基本面"].dropna()
                if len(basics_column) > 0:
                    try:
                        basics_value = json.loads(basics_column.iloc[0])
                        if isinstance(basics_value, str) and basics_value == "数据不可用":
                            basics_unavailable += 1
                            total_files += 1
                            continue
                        elif isinstance(basics_value, dict) and basics_value.get("数据不可用"):
                            basics_unavailable += 1
                            total_files += 1
                            continue
                    except:
                        pass

            total_files += 1
            normal_data += 1

        print(f"数据可用且基本面正常: {normal_data}")
        print(f"数据可用但基本面不可用: {basics_unavailable}")
        print(f"数据不可用: {data_unavailable}\n")

    else:
        print(f"data/stock_info 不存在\n")

