import numpy as np
from sklearn.metrics import mean_absolute_percentage_error

from cases.model_settings import MODEL_CONSTRUCTOR, PRED_DAYS, INFER_DAYS


class CombiModel:

    def __init__(self, constructor=MODEL_CONSTRUCTOR):
        self.models = [constructor()for i in range(PRED_DAYS + INFER_DAYS)]

    def fit(self, train_features, train_labels):
        for i, model in enumerate(self.models):
            print(f"Model {i}")
            model.fit(np.array(train_features.values), np.array(train_labels[[f"t_{i}"]]).reshape(-1))

    def evaluate(self, test_features, test_labels):
        scores = []
        mean_errors = []
        for i, model in enumerate(self.models):
            score = model.score(np.array(test_features), test_labels[[f"t_{i}"]])
            scores.append(score)
            mean_error = mean_absolute_percentage_error(test_labels[[f"t_{i}"]], model.predict(np.array(test_features)))
            mean_errors.append(1 - mean_error)

        print(scores)
        return scores, mean_errors

    def predict(self, features):
        preds_all = [model.predict(np.array(features.iloc[0, :]).reshape(1, -1), return_std=True)
                     for model in self.models]
        return [x[0] for x in preds_all], [x[1] for x in preds_all]
