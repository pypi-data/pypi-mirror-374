import datetime
import re
import requests
import zipfile
from io import BytesIO, StringIO

import pandas as pd
from sangreal_wind.crawler.futures import domestic_cons as cons

calendar = cons.get_calendar()


def get_cffex_daily(date: str = "20100416") -> pd.DataFrame:
    """
    中国金融期货交易所-日频率交易数据
    http://www.cffex.com.cn/rtj/
    :param date: 交易日; 数据开始时间为 20100416
    :type date: str
    :return: 日频率交易数据
    :rtype: pandas.DataFrame
    """
    day = (cons.convert_date(date)
           if date is not None else datetime.date.today())
    if day.strftime("%Y%m%d") not in calendar:
        # warnings.warn("%s非交易日" % day.strftime("%Y%m%d"))
        return None
    url = (
        f"http://www.cffex.com.cn/sj/historysj/{date[:-2]}/zip/{date[:-2]}.zip"
    )
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    r = requests.get(url, headers=headers)
    try:
        with zipfile.ZipFile(BytesIO(r.content)) as file:
            with file.open(f"{date}_1.csv") as my_file:
                data = my_file.read().decode("gb2312")
                data_df = pd.read_csv(StringIO(data))
    except:
        return None
    data_df = data_df[data_df["合约代码"] != "小计"]
    data_df = data_df[data_df["合约代码"] != "合计"]
    data_df = data_df[~data_df["合约代码"].str.contains("IO")]
    data_df = data_df[~data_df["合约代码"].str.contains("MO")]
    data_df = data_df[~data_df["合约代码"].str.contains("HO")]
    data_df.reset_index(inplace=True, drop=True)
    data_df["合约代码"] = data_df["合约代码"].str.strip()
    symbol_list = data_df["合约代码"].to_list()
    variety_list = [
        re.compile(r"[a-zA-Z_]+").findall(item)[0] for item in symbol_list
    ]
    if data_df.shape[1] == 15:
        data_df.columns = [
            "symbol",
            "open",
            "high",
            "low",
            "volume",
            "turnover",
            "open_interest",
            "_",
            "close",
            "settle",
            "pre_settle",
            "_",
            "_",
            "_",
            "_",
        ]
    else:
        data_df.columns = [
            "symbol",
            "open",
            "high",
            "low",
            "volume",
            "turnover",
            "open_interest",
            "_",
            "close",
            "settle",
            "pre_settle",
            "_",
            "_",
            "_",
        ]
    data_df["date"] = date
    data_df["variety"] = variety_list
    data_df = data_df[[
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "open_interest",
        "turnover",
        "settle",
        "pre_settle",
        "variety",
    ]]
    return data_df
