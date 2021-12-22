import numpy as np
import pandas as pd
from sklearn.linear_model import BayesianRidge, ARDRegression, LinearRegression
from sklearn.model_selection import KFold, train_test_split

from cases.CombiModel import CombiModel
from cases.train_model import get_archive_data, train_model, evaluate_models
from cases.model_settings import *

import os

os.chdir("..")


models = {
    "bayes":    lambda: BayesianRidge(),
    "ard":      lambda: ARDRegression(),
    "linear":   lambda: LinearRegression(),
}

results = {}

data = pd.read_csv(TRAINING_DATA_PATH)
features = data[[f"{i}" for i in range(BACK_DAYS + INFER_DAYS + PUB_DAYS + 3)]]
targets = data[[f"t_{i}" for i in range(PRED_DAYS + INFER_DAYS + 1)]]

train_features, test_features, train_labels, test_labels = \
    train_test_split(features, targets, test_size=0.1)


for name, constructor in models.items():
    kf = KFold(n_splits=6)

    all_scores = []

    for train_index, test_index in kf.split(train_features, train_labels):
        fold_features = train_features.iloc[train_index]
        fold_labels = train_labels.iloc[train_index]

        fold_test_features = train_features.iloc[test_index]
        fold_test_labels = train_labels.iloc[test_index]

        model = CombiModel(constructor)
        train_model(fold_features, fold_labels, model)
        scores, mean_errors = evaluate_models(model, fold_test_features, fold_test_labels)
        all_scores.append(np.mean(np.array(scores) ** 2))

    results[name] = np.mean(all_scores)

print(results)

