import akshare_proxy_patch

def get_symbol_info():

  print("正在获取并写入股票代码至data/A_stock_list.csv:")

  akshare_proxy_patch.install_patch(
      "101.201.173.125",
      auth_token="202605131EBUA4VT",
      retry=30,
      hook_domains=[
        "fund.eastmoney.com",
        "push2.eastmoney.com",
        "push2his.eastmoney.com",
        "emweb.securities.eastmoney.com",
      ],
  )

  import akshare as ak

  df = ak.stock_zh_a_spot_em()
  result = df[["代码", "名称" ]]

  result.to_csv("data/A_stock_list.csv", index = False, encoding = "utf-8-sig")
