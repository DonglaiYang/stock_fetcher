# 使akshare用代理服务器进行请求
import akshare_proxy_patch

akshare_proxy_patch.install_patch(
    "101.201.173.125",
    auth_token = "202605131EBUA4VT",
    retry = 30,
    hook_domains = [
      "fund.eastmoney.com",
      "push2.eastmoney.com",
      "push2his.eastmoney.com",
      "emweb.securities.eastmoney.com",
    ],
)

import os
import json
import math
import pandas as pd
import akshare as ak
from tqdm import tqdm
from utils import get_symbol_info, get_news_info, data_check

START_DATE = "20250517"
END_DATE = "20260517"

def get_company_info(symbol, close):
    company_info = ak.stock_individual_info_em(symbol = symbol)
    info_dict = {}
    for _, row in company_info.iterrows():
        info_dict[row["item"]] = row["value"]
    info_dict.pop("最新", None) 
    info_dict["上市时间"] = pd.to_datetime(info_dict["上市时间"], format="%Y%m%d").strftime("%Y-%m-%d")
    company_info_json = json.dumps(info_dict, ensure_ascii = False)
    return [company_info_json] * len(close)

def get_basics_info(symbol, close):
    try:
        financial_df = ak.stock_financial_abstract_ths(symbol = symbol, indicator = "按单季度")
        key_fields = ["报告期", "净利润同比增长率", "营业总收入同比增长率", 
                    "流动比率", "速动比率", "资产负债率"]
        financials = []
        for _, row in financial_df.iterrows():
            item = {}
            for field in key_fields:
                if field in row and pd.notna(row[field]):
                    item[field] = row[field]
            if item:
                item["报告期"] = row["报告期"]
                financials.append(item)
            
        basics_list = []
        fin_index = 0  

        for end_date in close.index:      
            while (fin_index + 1 < len(financials) and
                pd.to_datetime(financials[fin_index + 1]["报告期"]) < end_date):
                fin_index += 1

            matched = financials[fin_index] if financials else {}
            basics_list.append(json.dumps(matched, ensure_ascii = False))
        
        return basics_list
    
    except Exception:
        return [json.dumps("数据不可用")] * len(close)

def get_start_time(close):
    return close.index - pd.Timedelta(days = 4)

def get_end_time(close):
    return close.index

def get_opening_price(close):
    return close.shift(1).values

def get_settlement_price(close):
    return close.values

def get_returns_info(close):
    return close.pct_change()

def get_up_down_info(close):
    up_down_data = []
    for value in close.pct_change().values:
        if pd.isna(value):
            up_down_data.append(None)
            continue
        if abs(value) < 0.005:
            up_down_data.append("平")
            continue
        up_or_down = "涨" if value > 0 else "跌"
        num = math.ceil(abs(100 * value))
        up_down_data.append(up_or_down + (str(num) if num <= 5 else "5+"))
    return up_down_data

def get_weekly_data(symbol, start_date, end_date):
    
    df = ak.stock_zh_a_hist(
        symbol = symbol,
        period = "daily",
        start_date = start_date,
        end_date = end_date,
        adjust = "qfq"
    )
    if df.empty:
        return pd.DataFrame({"数据可用": [False]})
        
    # 以收盘日期作重采样
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.set_index("日期")
    close = df["收盘"].resample("W").last()

    # dataframe
    weekly_data = pd.DataFrame({
        "数据可用": [True] * len(close),
        "公司信息": get_company_info(symbol, close),
        "基本面": get_basics_info(symbol, close),
        "起始日期": get_start_time(close),
        "结算日期": get_end_time(close),                          
        "起始价": get_opening_price(close), 
        "结算价": get_settlement_price(close),
        "周收益率": get_returns_info(close),
        "涨跌标签": get_up_down_info(close)
    })

    # 去掉第一周的数据
    weekly_data = weekly_data.iloc[1:]
    weekly_data = weekly_data.reset_index(drop=True)

    return weekly_data

def process_stock(symbol, start_date, end_date, output_dir):

    output_path = os.path.join(output_dir, f"{symbol}.csv")
    if os.path.exists(output_path):
        return
    weekly_data = get_weekly_data(symbol, start_date, end_date)
    os.makedirs(output_dir, exist_ok = True)
    weekly_data.to_csv(output_path, index = False, encoding="utf-8-sig")

if __name__ == "__main__":

    os.makedirs("data", exist_ok = True)
    os.makedirs("data/stock_info", exist_ok = True)
    
    # get_symbol_info()

    df = pd.read_csv("data/A_stock_list.csv", dtype = {"代码": str})
    stock_list = list(zip(df["代码"], df["名称"]))

    # get_news_info(df)

    print("正在获取并写入股票信息至data/stock_info:")
    for symbol, name in tqdm(stock_list): process_stock(
        symbol = symbol,
        start_date = START_DATE,
        end_date = END_DATE,
        output_dir = "data/stock_info"
    )
    
    data_check()