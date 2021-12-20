from urllib.error import HTTPError
import pandas as pd
import datetime as dt
import os
import time
from cases.model_settings import ARCHIVE_URL_SCHEME, ARCHIVE_PATH


def update_archive():
    start_date = dt.date.today()
    for i in range(0, 225):
        date = start_date - dt.timedelta(days=i)
        d = f"{ARCHIVE_PATH}/{date.year}-{date.month}-{date.day}"
        print(date)
        if os.path.exists(d):
            print("  Skipping")
            continue
        URL = ARCHIVE_URL_SCHEME.format(date.year, date.month, date.day)
        try:
            df = pd.read_csv(URL)
            df.to_csv(f"{ARCHIVE_PATH}/{date.year}-{date.month}-{date.day}")
            time.sleep(11)
        except HTTPError as e:
            print(e)
