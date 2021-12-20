import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cases.Dates import Dates, calculate_dates
from cases.data import get_features, get_latest_data


def predict(model, latest_spec, latest_pub, dates: Dates):
    latest_features = get_features(latest_spec, latest_pub, dates)
    return model.predict(latest_features)


def make_graph(preds, preds_std, latest_spec, latest_pub, dates: Dates):
    preds_dates = dates.prediction_dates()

    df_all = latest_spec.loc[dates.incomplete_start_date:].append(
        pd.DataFrame({"date": np.array(preds_dates).ravel(), "newCasesBySpecimenDate": np.array(preds).ravel()})
            .set_index(["date"])
    ).sort_index()
    df_all["mvavg"] = df_all.rolling(window=7)["newCasesBySpecimenDate"].mean()

    back_data_spec = latest_spec.loc[dates.incomplete_start_date: dates.feature_start_date - dt.timedelta(days=10)]
    back_data_pub = latest_pub.loc[dates.publish_start_date: dates.incomplete_start_date]
    unconfirmed = latest_spec.loc[dates.data_start_date: dates.incomplete_start_date]

    monday = dt.date.today() + dt.timedelta(days=-dt.date.today().weekday(), weeks=1)

    errors_lower = [float(p - 3 * s) for p, s in zip(preds, preds_std)]
    errors_upper = [float(p + 3 * s) for p, s in zip(preds, preds_std)]

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    plt.fill_between(preds_dates, errors_lower, errors_upper, color="grey", alpha=0.5, label="± 3sd")
    plt.axvline(monday, color="darkgrey", alpha=0.5)
    plt.axvline(monday - dt.timedelta(weeks=1), color="darkgrey", alpha=0.5)

    plt.plot(df_all.loc[dates.feature_start_date - dt.timedelta(days=10):dates.incomplete_start_date]["mvavg"],
             linestyle=":",
             label="7 Day Moving Avg.", color="blue")
    plt.plot(df_all.loc[dates.incomplete_start_date:]["mvavg"], linestyle=":", label="7 Day Moving Avg. (Predicted)",
             color="red")

    plt.scatter(back_data_spec.index, back_data_spec, marker="x", color="b", label="Actual Cases")

    plt.scatter(preds_dates, preds, marker="o", edgecolors="r", facecolors="none", label="Predictions")

    plt.legend()
    date = dt.date.today()
    d = f"{date.year}-{date.month}-{date.day}"
    plt.title(f"Predicted Cases by Specimen Date {d}")

    fig.savefig("out/model_out.png", pad_inches=0.05, transparent=False, dpi=300)
    fig.savefig(f"out/models/{d}.png", pad_inches=0.05, transparent=False, dpi=300)

    back_data_spec = latest_spec.loc[
                     dates.feature_start_date - dt.timedelta(days=10): dates.feature_start_date - dt.timedelta(
                         days=150)]
    plt.plot(
        df_all.loc[dates.feature_start_date - dt.timedelta(days=150):dates.feature_start_date - dt.timedelta(days=10)][
            "mvavg"], linestyle=":",
        label="7 Day Moving Avg.", color="blue")
    plt.scatter(back_data_spec.index, back_data_spec, marker="x", color="b")
    ax.set_ylim(0, max(max(errors_upper), max(back_data_spec["newCasesBySpecimenDate"])) * 1.1)
    fig.savefig(f"out/models/all-{d}.png", pad_inches=0.05, transparent=False, dpi=300)


def create_prediction(model):
    latest_spec, latest_pub = get_latest_data()
    dates = calculate_dates(latest_spec, latest_pub)
    preds, preds_std = predict(model, latest_spec, latest_pub, dates)
    make_graph(preds, preds_std, latest_spec, latest_pub, dates)
