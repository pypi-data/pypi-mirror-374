'''
Created on 2017年06月04日
@author: debugo
@contact: me@debugo.com
'''
import re
import json
import os
import datetime

DATE_PATTERN = re.compile(r"^([0-9]{4})[-/]?([0-9]{2})[-/]?([0-9]{2})")


def convert_date(date):
    """
    transform a date string to datetime.date object
    :param date, string, e.g. 2016-01-01, 20160101 or 2016/01/01
    :return: object of datetime.date(such as 2016-01-01) or None
    """
    if isinstance(date, datetime.date):
        return date
    elif isinstance(date, str):
        match = DATE_PATTERN.match(date)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                return datetime.date(
                    year=int(groups[0]),
                    month=int(groups[1]),
                    day=int(groups[2]),
                )
    return None


def get_calendar():
    """
    获取交易日历, 这里的交易日历需要按年更新, 主要是从新浪获取的
    :return: 交易日历
    :rtype: json
    """
    from sangreal_wind.sangreal_calendar import get_trade_dts
    data_json = get_trade_dts().to_list()
    return data_json
