import datetime as dt
import os

import pandas as pd

from cases.Dates import calculate_dates
from cases.data import select_features, get_features, get_latest_data
from cases.model_settings import *


def clean_data(path=TRAINING_DATA_PATH):
    start_date = dt.date.today()

    data = pd.DataFrame()
    # date = dt.date.today()
    # d = f"{date.year}-{date.month}-{date.day}"

    latest, _ = get_latest_data()

    # latest = pd.read_csv(f"{ARCHIVE_PATH}/{d}")
    # latest["date"] = pd.to_datetime(latest["date"])
    # latest = latest.set_index(["date"])

    for i in range(PRED_DAYS + INFER_DAYS + 1, 400):
        date = start_date - dt.timedelta(days=i)
        date_str = f"{date.year}-{date.month}-{date.day}"
        path = f"{ARCHIVE_PATH}/{date_str}"

        if not os.path.exists(path):
            print(f"Skipping {date}")
            continue

        snapshot = pd.read_csv(path)[["newCasesBySpecimenDate", "newCasesByPublishDate", "date"]]
        snapshot["date"] = pd.to_datetime(snapshot["date"])
        snapshot = snapshot.set_index(["date"])

        df_specdate = snapshot[["newCasesBySpecimenDate"]].dropna()
        df_pubdate = snapshot[["newCasesByPublishDate"]].dropna()

        dates = calculate_dates(df_specdate, df_pubdate)
        df_features = get_features(df_specdate, df_pubdate, dates)

        targets = latest.loc[dates.predict_end_date:dates.incomplete_start_date, ["newCasesBySpecimenDate"]] \
            .transpose().reset_index().drop(["index"], axis=1)

        # t_0 is the correct answer for the most recent day day
        targets = targets.rename(columns={x: f"t_{y}" for x, y in zip(targets.columns, range(0, len(targets.columns)))})

        df_final = df_features.join(targets)
        data = data.append(df_final, True)

    print(data)
    data.to_csv(TRAINING_DATA_PATH)
