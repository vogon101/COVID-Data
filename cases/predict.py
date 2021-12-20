import matplotlib.pyplot as plt
from cases.model_settings import *
from cases.clean_data import select_features
import numpy as np
import datetime as dt
import pandas as pd
import matplotlib as mpl
import matplotlib.collections, matplotlib.dates


def get_latest_data():
    URL = \
        "https://api.coronavirus.data.gov.uk/v2/data?" \
        "areaType=overview&metric=newCasesBySpecimenDate&metric=newCasesByPublishDate" \
        "&format=csv"
    latest = pd.read_csv(URL)
    latest["date"] = pd.to_datetime(latest["date"])
    latest = latest.set_index(["date"])
    latest_spec = latest[["newCasesBySpecimenDate"]].dropna()
    latest_pub = latest[["newCasesByPublishDate"]].dropna()
    return latest_spec, latest_pub


def predict(models):
    latest_spec, latest_pub = get_latest_data()

    data_start_date = max(latest_spec.index)
    dow = data_start_date.weekday()
    incomplete_start_date = data_start_date - dt.timedelta(days=INFER_DAYS)
    feature_start_date = incomplete_start_date - dt.timedelta(days=BACK_DAYS)
    predict_end_date = data_start_date + dt.timedelta(days=PRED_DAYS)
    publish_start_date = max(latest_pub.index)
    publish_end_date = publish_start_date - dt.timedelta(days=PUB_DAYS)

    print(f"Features from {feature_start_date}")
    print(f"Incomplete from {incomplete_start_date} to {data_start_date}")
    print(f"Published data from {publish_start_date} to {publish_end_date}")
    print(f"Predicting to {predict_end_date}")

    features_spec = select_features(latest_spec, data_start_date, feature_start_date)
    features_spec[f"{len(features_spec.columns)}"] = [dow]
    features_pubdate = select_features(latest_pub, publish_start_date, publish_end_date, offset=len(features_spec.columns))
    latest_features = features_spec.join(features_pubdate)

    preds_dates = [data_start_date - dt.timedelta(days=i) for i in range(-INFER_DAYS, PRED_DAYS)]
    preds_all = [model.predict(np.array(latest_features.iloc[0, :]).reshape(1, -1), return_std=True) for model in models]
    preds = [x[0] for x in preds_all]
    preds_std = [x[1] for x in preds_all]

    back_data_spec = latest_spec.loc[incomplete_start_date : feature_start_date-dt.timedelta(days=10)]
    back_data_pub = latest_pub.loc[publish_start_date : incomplete_start_date]
    unconfirmed = latest_spec.loc[data_start_date: incomplete_start_date]

    df_all = back_data_spec.append(
        pd.DataFrame({"date": np.array(preds_dates).ravel(), "newCasesBySpecimenDate": preds})
            .set_index(["date"])
    ).sort_index()
    df_all["mvavg"] = df_all.rolling(window=7)["newCasesBySpecimenDate"].mean()

    monday = dt.date.today() + dt.timedelta(days=-dt.date.today().weekday(), weeks=1)

    errors_lower = [float(p - 3 * s) for p, s in zip(preds, preds_std)]
    errors_upper = [float(p + 3 * s) for p, s in zip(preds, preds_std)]

    fig = plt.figure(figsize=(15,10))
    ax = fig.add_subplot(111)

    plt.fill_between(preds_dates, errors_lower, errors_upper, color="grey", alpha=0.5, label="± 3sd")
    plt.axvline(monday, color="darkgrey", alpha=0.5)
    plt.axvline(monday - dt.timedelta(weeks=1), color="darkgrey", alpha=0.5)

    plt.plot(df_all.loc[feature_start_date:incomplete_start_date]["mvavg"], linestyle=":", label="7 Day Moving Avg.", color="blue")
    plt.plot(df_all.loc[incomplete_start_date:]["mvavg"], linestyle=":", label="7 Day Moving Avg. (Predicted)",
             color="red")

    plt.scatter(back_data_spec.index, back_data_spec, marker="x", color="b", label="Actual Cases")
    plt.scatter(back_data_pub.index, back_data_pub, marker="x", color="black", label="Published Cases", alpha=0.5)
    plt.scatter(unconfirmed.index, unconfirmed, marker="x", color="g", label="Unconfirmed Case Data")
    plt.scatter(preds_dates, preds, marker="o", edgecolors="r", facecolors="none", label="Predictions")

    plt.legend()
    date = dt.date.today()
    d = f"{date.year}-{date.month}-{date.day}"
    plt.title(f"Predicted Cases by Specimen Date {d}")

    fig.savefig("out/model_out.png", pad_inches=0.05, transparent=False, dpi=300)
    fig.savefig(f"out/models/{d}.png", pad_inches=0.05, transparent=False, dpi=300)

    back_data_spec = latest_spec.loc[feature_start_date-dt.timedelta(days=10): feature_start_date-dt.timedelta(days=150)]
    plt.scatter(back_data_spec.index, back_data_spec, marker="x", color="b")
    ax.set_ylim(0, max(max(errors_upper), max(back_data_spec["newCasesBySpecimenDate"])) * 1.1)
    fig.savefig(f"out/models/all-{d}.png", pad_inches=0.05, transparent=False, dpi=300)