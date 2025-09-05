from sangreal_wind.utils.engines import WIND_DB

from sangreal_calendar import *


def tmp_data():
    table = WIND_DB.ASHARECALENDAR
    df = WIND_DB.query(
        table.TRADE_DAYS.label('t')).filter(table.S_INFO_EXCHMARKET == 'SSE').order_by(
            table.TRADE_DAYS).to_df()
    return df['t']


CALENDAR.inject(tmp_data())
DELISTDATE = get_delistdate_all()
DELISTDATE_TF = get_delistdate_tf_all()
