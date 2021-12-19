import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import BayesianRidge, ARDRegression
from sklearn.ensemble import RandomForestRegressor
import datetime as dt

URL = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesByPublishDate&metric=newCasesByPublishDateChange&metric=newCasesBySpecimenDate&metric=newCasesBySpecimenDateChange&format=csv"

data = pd.read_csv(URL)
data = data[3:-500]
data["date"] = pd.to_datetime(data['date'])
data["ts"] = data["date"].values.astype(np.int64) // 10 ** 9
data = data.drop(["areaCode", "areaType", "areaName"], axis=1)
data = data.set_index(["date"])

print(data["newCasesBySpecimenDate"][:5])
plt.bar(data.index[5:20], data["newCasesBySpecimenDate"][5:20])
plt.bar(data.index[:5], data["newCasesBySpecimenDate"][:5])


NORM_COEFF = np.mean(data["newCasesBySpecimenDate"])
data["newCasesBySpecimenDateNorm"] = data["newCasesBySpecimenDate"] / NORM_COEFF
data["newCasesBySpecimenDateLog"] = np.log(data["newCasesBySpecimenDateNorm"])
data["newCasesBySpecimenDateMovingAvg"] = data["newCasesBySpecimenDate"].rolling(7).sum()/7
data["target"] = data["newCasesBySpecimenDate"].shift(-1, "infer")

data = data.dropna()

# features = data.drop(["target", "ts"], axis=1)
features = data[["newCasesBySpecimenDateNorm", "newCasesBySpecimenDateLog"]]
train_features, test_features, train_labels, test_labels = \
    train_test_split(features, data["target"], test_size=0.1)


# model = RandomForestRegressor()
model = BayesianRidge()
model.fit(train_features, train_labels)
preds = model.predict(test_features)
errors = (preds - test_labels)
mape = 100 * (errors / test_labels)
accuracy = 100 - np.mean(mape)
print(accuracy)

# data.info()
plt.figure(figsize=(8, 6), dpi=100)

# plt.scatter(train_features["ts"], train_labels, alpha=0.3, marker="x")
# plt.scatter(test_features["ts"], test_labels, marker="x")
# plt.scatter(test_features["ts"], preds, marker="x")

SELECT = 100

preds, preds_err = model.predict(features.to_numpy(), return_std=True)
errors = preds - data["target"]
plt.scatter(data.index[:SELECT], data["target"][:SELECT], marker="o", facecolor="none", edgecolors="b")
plt.scatter(data.index[:SELECT], preds[:SELECT], marker="x", color="r")
# plt.errorbar(data.index[:SELECT], preds[:SELECT], yerr=preds_err[:SELECT],
#              marker="x", ecolor="grey", alpha=0.1, capsize=0, linestyle="", color="red")

START = 10
PREDICT = 7
last_day = data.index[START]
predict_dates = [last_day + dt.timedelta(days=i) for i in range(0, PREDICT)]
lowers, uppers = [], []
predictions = []
predictions_err = []
upper = float(data["newCasesBySpecimenDate"][START])
lower = float(data["newCasesBySpecimenDate"][START])

for date in predict_dates:
    print(upper, lower)

    v_upper, s_upper = model.predict(np.array([upper / NORM_COEFF, np.log(upper/NORM_COEFF)]).reshape(1, -1), True)
    v_lower, s_lower = model.predict(np.array([lower / NORM_COEFF, np.log(lower/NORM_COEFF)]).reshape(1, -1), True)

    lowers.append(float(v_lower))
    uppers.append(float(v_upper))

    v = (v_upper + v_lower) / 2
    predictions.append(v)
    predictions_err.append([v - (v_lower - float(s_lower)), v_upper + float(s_upper) - v])

    upper = v_upper + s_upper
    lower = v_lower - s_lower

predictions_err = np.array(predictions_err).reshape(2,-1)
print(predictions_err)
# plt.errorbar(predict_dates, predictions, yerr=predictions_err, marker="x", linestyle="none")
plt.fill_between(predict_dates, lowers, uppers, color="grey", alpha=0.5)

N = len(preds) - SELECT



# plt.plot(data["ts"][:SELECT], np.convolve(data["target"][:SELECT], np.ones(4)/4, mode="same"))
# plt.plot(data["ts"][:SELECT], np.convolve(preds[:SELECT], np.ones(4)/4, mode="same"))

plt.legend()
plt.show()

features.info()
# Get numerical feature importances
importances = list(model.coef_)
# List of tuples with variable and importance
feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(features.keys(), importances)]
# Sort the feature importances by most important first
feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
# Print out the feature and importances
[print('Variable: {:20} Coeff: {}'.format(*pair)) for pair in feature_importances];