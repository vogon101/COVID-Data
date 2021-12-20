import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_percentage_error
from cases.model_settings import *


def get_archive_data():
    data = pd.read_csv(TRAINING_DATA_PATH)
    features = data[[f"{i}" for i in range(BACK_DAYS + INFER_DAYS + PUB_DAYS + 3)]]
    targets = data[[f"t_{i}" for i in range(PRED_DAYS + INFER_DAYS + 1)]]
    print(features)
    print(targets)

    train_features, test_features, train_labels, test_labels = \
        train_test_split(features, targets, test_size=0.1)

    print(train_features.shape)
    print(train_labels.shape)
    print(test_features.shape)
    print(test_labels.shape)
    return data, (train_features, train_labels), (test_features, test_labels)


def train_model(train_features, train_labels):
    models = [MODEL_CONSTRUCTOR() for i in range(PRED_DAYS + INFER_DAYS)]
    for i, model in enumerate(models):
        print(f"Model {i}")
        model.fit(np.array(train_features.values), np.array(train_labels[[f"t_{i}"]]).reshape(-1))
    return models


def evaluate_models(models, test_features, test_labels):
    scores = []
    mean_errors = []
    for i, model in enumerate(models):
        score = model.score(np.array(test_features), test_labels[[f"t_{i}"]])
        scores.append(score)
        mean_error = mean_absolute_percentage_error(test_labels[[f"t_{i}"]], model.predict(np.array(test_features)))
        mean_errors.append(1 - mean_error)

    print(scores)
    return scores, mean_errors


def do_train_model():
    data, train, test = get_archive_data()
    models = train_model(train[0], train[1])
    scores, mean_errors = evaluate_models(models, test[0], test[1])

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
    return models

