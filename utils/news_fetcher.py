import pandas as pd
import requests
import json
import time
import re
from tqdm import tqdm

def _clean_tags(text):
    return re.sub(r"<[^>]+>", "", text)

def _fetch_news_from_eastmoney(keyword):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://so.eastmoney.com/",
    }

    param = {
        "uid": "",
        "keyword": keyword,
        "type": ["cmsArticleWebOld"],
        "client": "web",
    }

    url = (
        f"https://search-api-web.eastmoney.com/search/jsonp"
        f"?cb=jQuery"
        f"&param={json.dumps(param, ensure_ascii = False)}"
        f"&page=1&size=10"
    )

    try:
        resp = requests.get(url, headers = headers, timeout = 10)
        text = resp.text
        start = text.index("(") + 1
        end = text.rindex(")")
        data = json.loads(text[start:end])
        articles = data.get("result", {}).get("cmsArticleWebOld", [])

        all_news = []
        for art in articles:
            all_news.append({
                "date": art["date"],
                "title": _clean_tags(art["title"]),
                "content": _clean_tags(art["content"]),
            })
        return all_news

    except Exception:
        return []


def get_news_info(df):

    stock_list = list(zip(df["代码"], df["名称"]))

    all_news_rows = []

    print("正在获取并写入股票新闻至data/stock_info:")
    for symbol, name in tqdm(stock_list):
        news = _fetch_news_from_eastmoney(name)
        for n in news:
            all_news_rows.append({
                "股票代码": symbol,
                "股票名称": name,
                "新闻标题": n["title"],
                "新闻内容": n["content"],
                "发布时间": n["date"],
            })
        time.sleep(0.3)

    result = pd.DataFrame(all_news_rows)

    result.to_csv("data/stock_info/all_news.csv", index = False, encoding = "utf-8-sig")