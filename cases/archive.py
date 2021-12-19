from urllib.error import HTTPError

import numpy as download_archive
import pandas as pd
import datetime as dt
import os
import time

URL_SCHEME = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesBySpecimenDate&metric=newCasesBySpecimenDateChange&metric=newCasesBySpecimenDateRollingRate&metric=newCasesByPublishDateChangePercentage&format=csv&release={:4d}-{:02d}-{:02d}"

START_DATE = dt.date.today()
for i in range(0, 225):
    date = START_DATE - dt.timedelta(days=i)
    d = f"cases/data/{date.year}-{date.month}-{date.day}"
    print(date)
    if os.path.exists(d):
        print("  Skipping")
        continue
    URL = URL_SCHEME.format(date.year, date.month, date.day)
    try:
        df = pd.read_csv(URL)
        df.to_csv(f"cases/data/{date.year}-{date.month}-{date.day}")
        time.sleep(11)
    except HTTPError as e:
        print(e)
