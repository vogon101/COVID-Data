import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import BayesianRidge
from sklearn.metrics import mean_absolute_percentage_error

INFER_DAYS = 5
PRED_DAYS = 5
BACK_DAYS = 30

URL = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesBySpecimenDate&format=csv"
latest = pd.read_csv(URL)
latest["date"] = pd.to_datetime(latest["date"])
latest = latest.set_index(["date"])[["newCasesBySpecimenDate"]].dropna()


print(latest)

data = pd.read_csv("cases/training_data.csv")
features = data[[f"{i}" for i in range(BACK_DAYS + PRED_DAYS + 1)]]
targets = data[[f"t_{i}" for i in range(PRED_DAYS + INFER_DAYS + 1)]]
print(features)
print(targets)

train_features, test_features, train_labels, test_labels = \
    train_test_split(features, targets, test_size=0.1)

print(train_features.shape)
print(train_labels.shape)
print(test_features.shape)
print(test_labels.shape)

models = [BayesianRidge() for i in range(PRED_DAYS + INFER_DAYS)]
scores = []
mean_errors = []
for i, model in enumerate(models):
    print(f"Model {i}")
    model.fit(np.array(train_features.values), np.array(train_labels[[f"t_{i}"]]).reshape(-1))
    score = model.score(np.array(test_features), test_labels[[f"t_{i}"]])
    scores.append(score)
    mean_error = mean_absolute_percentage_error(test_labels[[f"t_{i}"]], model.predict(np.array(test_features)))
    mean_errors.append(1 - mean_error)
print(scores)

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

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

plt.scatter([i for i in range(PRED_DAYS, -INFER_DAYS, -1)], scores, marker="x", color="red", label="R^2")
plt.scatter([i for i in range(PRED_DAYS, -INFER_DAYS, -1)], mean_errors, marker="x", color="green", label="MAPE")


plt.title("Model Evaluation")
plt.ylim(0,1.05)
plt.legend(loc="lower left")
plt.axvline(0, color="grey", linestyle=":")
plt.axhline(1, color="grey", linestyle=":")
plt.savefig("out/model_scores.png")

fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)

plt.scatter(back_data.index, back_data, marker="x", color="b", label="Actual Cases")
plt.scatter(unconfirmed.index, unconfirmed, marker="x", color="g", label="Unconfirmed Case Data")
plt.scatter(preds_dates, preds, marker="o", edgecolors="r", facecolors="none", label="Predictions")

monday = dt.date.today() + dt.timedelta(days=-dt.date.today().weekday(), weeks=1)

errors_lower = [float(p - 3 * s) for p, s in zip(preds, preds_std)]
errors_upper = [float(p + 3 * s) for p, s in zip(preds, preds_std)]

plt.fill_between(preds_dates, errors_lower, errors_upper, color="grey", alpha=0.5, label="± 3sd")
plt.axvline(monday, color="darkgrey", alpha=0.5)
plt.axvline(monday - dt.timedelta(weeks=1), color="darkgrey", alpha=0.5)

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