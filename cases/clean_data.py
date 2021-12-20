import pandas as pd
import os
import datetime as dt
import numpy as np

from cases.model_settings import *


def select_features(df, start, end, offset=0):
    df = df.loc[start: end].transpose().reset_index()
    df = df.drop(["index"], axis=1)
    df = df.rename(
        columns={x:(y + offset) for x, y in zip(df.columns, range(0, len(df.columns)))})
    return df


def clean_data(path=TRAINING_DATA_PATH):
    start_date = dt.date.today()

    data = pd.DataFrame()
    date = dt.date.today()
    d = f"{date.year}-{date.month}-{date.day}"

    latest = pd.read_csv(f"{ARCHIVE_PATH}/{d}")
    latest["date"] = pd.to_datetime(latest["date"])
    latest = latest.set_index(["date"])

    for i in range(15, 400):
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

        data_start_date = max(df_specdate.index)
        dow = data_start_date.weekday()
        incomplete_start_date = data_start_date - dt.timedelta(days=INFER_DAYS)
        feature_start_date = incomplete_start_date - dt.timedelta(days=BACK_DAYS)
        predict_end_date = data_start_date + dt.timedelta(days=PRED_DAYS)

        publish_start_date = max(df_pubdate.index)
        publish_end_date = publish_start_date - dt.timedelta(days=PUB_DAYS)

        print(f"Features from {feature_start_date}")
        print(f"Incomplete from {incomplete_start_date} to {data_start_date}")
        print(f"Published data from {publish_start_date} to {publish_end_date}")

        df_specdate = select_features(df_specdate, data_start_date, feature_start_date)
        df_specdate[f"{len(df_specdate.columns)}"] = [dow]
        df_pubdate = select_features(df_pubdate, publish_start_date, publish_end_date, offset=len(df_specdate.columns))
        df_features = df_specdate.join(df_pubdate)

        targets = latest.loc[predict_end_date:incomplete_start_date, ["newCasesBySpecimenDate"]]\
            .transpose().reset_index().drop(["index"], axis=1)

        # t_0 is the correct answer for the most recent day day
        targets = targets.rename(columns={x: f"t_{y}" for x,y in zip(targets.columns, range(0, len(targets.columns)))})

        df_final = df_features.join(targets)
        data = data.append(df_final, True)

    print(data)
    data.to_csv(TRAINING_DATA_PATH)