import matplotlib.pyplot as plt
from cases.model_settings import *
import numpy as np
import datetime as dt
import pandas as pd


def get_latest_data():
    URL = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesBySpecimenDate&format=csv"
    latest = pd.read_csv(URL)
    latest["date"] = pd.to_datetime(latest["date"])
    latest = latest.set_index(["date"])[["newCasesBySpecimenDate"]].dropna()
    return latest


def predict(models):
    latest = get_latest_data()

    data_start_date = max(latest.index)
    dow = data_start_date.weekday()
    incomplete_start_date = data_start_date - dt.timedelta(days=INFER_DAYS)
    feature_start_date = incomplete_start_date - dt.timedelta(days=BACK_DAYS - 1)
    predict_end_date = data_start_date + dt.timedelta(days=PRED_DAYS)

    print(f"Features from {feature_start_date}")
    print(f"Incomplete from {incomplete_start_date} to {data_start_date}")
    print(f"Predicting to {predict_end_date}")

    latest_features = latest.loc[data_start_date : feature_start_date].transpose().reset_index()
    latest_features = latest_features.drop(["index"], axis=1)
    latest_features = latest_features.rename(
        columns={x:y for x,y in zip(latest_features.columns, range(0, len(latest_features.columns)))}
    )
    latest_features[f"{len(latest_features.columns)}"] = [dow]

    preds_dates = [data_start_date - dt.timedelta(days=i) for i in range(-INFER_DAYS, PRED_DAYS)]
    preds_all = [model.predict(np.array(latest_features.iloc[0, :]).reshape(1, -1), return_std=True) for model in models]
    preds = [x[0] for x in preds_all]
    preds_std = [x[1] for x in preds_all]

    back_data = latest.loc[incomplete_start_date : feature_start_date-dt.timedelta(days=10)]
    unconfirmed = latest.loc[data_start_date: incomplete_start_date]

    monday = dt.date.today() + dt.timedelta(days=-dt.date.today().weekday(), weeks=1)

    errors_lower = [float(p - 3 * s) for p, s in zip(preds, preds_std)]
    errors_upper = [float(p + 3 * s) for p, s in zip(preds, preds_std)]

    fig = plt.figure(figsize=(15,10))
    ax = fig.add_subplot(111)

    plt.fill_between(preds_dates, errors_lower, errors_upper, color="grey", alpha=0.5, label="± 3sd")
    plt.axvline(monday, color="darkgrey", alpha=0.5)
    plt.axvline(monday - dt.timedelta(weeks=1), color="darkgrey", alpha=0.5)

    plt.scatter(back_data.index, back_data, marker="x", color="b", label="Actual Cases")
    plt.scatter(unconfirmed.index, unconfirmed, marker="x", color="g", label="Unconfirmed Case Data")
    plt.scatter(preds_dates, preds, marker="o", edgecolors="r", facecolors="none", label="Predictions")

    plt.legend()
    date = dt.date.today()
    d = f"{date.year}-{date.month}-{date.day}"
    plt.title(f"Predicted Cases by Specimen Date {d}")

    fig.savefig("out/model_out.png", pad_inches=0.05, transparent=False, dpi=300)
    fig.savefig(f"out/models/{d}.png", pad_inches=0.05, transparent=False, dpi=300)

    back_data = latest.loc[feature_start_date-dt.timedelta(days=10): feature_start_date-dt.timedelta(days=150)]
    plt.scatter(back_data.index, back_data, marker="x", color="b")
    ax.set_ylim(0, max(max(errors_upper), max(back_data["newCasesBySpecimenDate"])) * 1.1)
    fig.savefig(f"out/models/all-{d}.png", pad_inches=0.05, transparent=False, dpi=300)