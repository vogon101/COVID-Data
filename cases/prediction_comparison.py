import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

from cases.data import get_latest_data
from cases.model_settings import PREDICTIONS_CSV_PATH, PRED_DAYS, INFER_DAYS


def compare_predictions():
    preds = pd.read_csv(PREDICTIONS_CSV_PATH)
    preds["date"] = pd.to_datetime(preds["date"])
    preds = preds.set_index(["date"])

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    start_date = min(preds.index)
    latest_spec = get_latest_data()[0].loc[start_date:start_date - dt.timedelta(days=20)]

    for date in preds.index:
        preds_dates = [date + dt.timedelta(days=i) for i in range(PRED_DAYS, -INFER_DAYS, -1)]

        df_all = latest_spec.loc[date - dt.timedelta(days=INFER_DAYS):].append(
            pd.DataFrame({"date": np.array(preds_dates).ravel(), "newCasesBySpecimenDate": np.array(preds.loc[date]).ravel()})
                .set_index(["date"])
        ).sort_index()

        df_all["mvavg"] = df_all.rolling(window=5)["newCasesBySpecimenDate"].mean()
        plt.plot(df_all["mvavg"], linestyle=":")

        d = {"date": [date + dt.timedelta(days=i) for i in range(PRED_DAYS, -INFER_DAYS, -1)]}
        d.update({"value": [preds.loc[date][i] for i in range(len(preds.columns))]})
        df = pd.DataFrame(d).set_index(["date"])
        plt.scatter(df.index, df["value"], label=date, marker="x")

    plt.legend()
    fig.savefig("out/model_comparison.png", pad_inches=0.05, transparent=False, dpi=300)
