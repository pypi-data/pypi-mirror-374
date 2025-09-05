import datetime
import zoneinfo


def datetime_now(timezone=None):
    """
    Memudahkan dalam membuat Datetime untuk suatu timezone tertentu

    ```python
    print(datetime_now("Asia/Jakarta"))
    print(datetime_now("GMT"))
    print(datetime_now("Etc/GMT+7"))
    ```
    """
    tz = zoneinfo.ZoneInfo(timezone) if timezone else None
    return datetime.datetime.now(tz)

