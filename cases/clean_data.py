import pandas as pd
import numpy as np
import os
import datetime as dt
import matplotlib.pyplot as plt



START_DATE = dt.date.today()

data = pd.DataFrame()
date = dt.date.today()
d = f"{date.year}-{date.month}-{date.day}"

latest = pd.read_csv(f"cases/data/{d}")
latest["date"] = pd.to_datetime(latest["date"])
latest = latest.set_index(["date"])

INFER_DAYS = 5
PRED_DAYS = 5
BACK_DAYS = 30

for i in range(15, 400):
    date = START_DATE - dt.timedelta(days=i)
    date_str = f"{date.year}-{date.month}-{date.day}"
    path = f"cases/data/{date_str}"

    if not os.path.exists(path):
        print(f"Skipping {date}")
        continue

    df = pd.read_csv(path)[["newCasesBySpecimenDate", "date"]].dropna()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index(["date"])

    data_start_date = max(df.index)
    dow = data_start_date.weekday()
    incomplete_start_date = data_start_date - dt.timedelta(days=INFER_DAYS)
    feature_start_date = incomplete_start_date - dt.timedelta(days=BACK_DAYS)
    predict_end_date = data_start_date + dt.timedelta(days=PRED_DAYS)

    print(f"Features from {feature_start_date}")
    print(f"Incomplete from {incomplete_start_date} to {data_start_date}")

    df = df.loc[data_start_date : feature_start_date].transpose().reset_index()
    df = df.drop(["index"], axis=1)
    df = df.rename(columns={x: y for x,y in zip(df.columns, range(0, len(df.columns)))})
    df[f"{len(df.columns)}"] = [dow]

    targets = latest.loc[predict_end_date:incomplete_start_date, ["newCasesBySpecimenDate"]]\
        .transpose().reset_index().drop(["index"], axis=1)

    # t_0 is the correct answer for the most recent day day
    targets = targets.rename(columns={x: f"t_{y}" for x,y in zip(targets.columns, range(0, len(targets.columns)))})

    df = df.join(targets)
    data = data.append(df, True)

print(data)
data.to_csv("cases/training_data.csv")