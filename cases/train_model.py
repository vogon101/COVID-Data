import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

from cases.CombiModel import CombiModel
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
    model = CombiModel()
    model.fit(train_features, train_labels)
    return model


def evaluate_models(model: CombiModel, test_features, test_labels):
    return model.evaluate(test_features, test_labels)


def do_train_model():
    data, train, test = get_archive_data()
    models = train_model(train[0], train[1])
    scores, mean_errors = evaluate_models(models, test[0], test[1])

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    plt.scatter([i for i in range(PRED_DAYS, -INFER_DAYS, -1)], scores, marker="x", color="red", label="R^2")
    plt.scatter([i for i in range(PRED_DAYS, -INFER_DAYS, -1)], mean_errors, marker="x", color="green", label="MAPE")
    plt.title("Model Evaluation")
    plt.ylim(0, 1.05)
    plt.legend(loc="lower left")
    plt.axvline(0, color="grey", linestyle=":")
    plt.axhline(1, color="grey", linestyle=":")
    plt.savefig("out/model_scores.png")
    return models
