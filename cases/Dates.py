import datetime as dt
from dataclasses import dataclass
from typing import List

import pandas as pd

from cases.model_settings import INFER_DAYS, PRED_DAYS, BACK_DAYS, PUB_DAYS


@dataclass
class Dates:
    data_start_date: dt.datetime
    incomplete_start_date: dt.datetime
    feature_start_date: dt.datetime
    predict_end_date: dt.datetime
    publish_start_date: dt.datetime
    publish_end_date: dt.datetime

    def prediction_dates(self) -> List[dt.datetime]:
        return [self.data_start_date + dt.timedelta(days=i) for i in range(PRED_DAYS, -INFER_DAYS, -1)]


def calculate_dates(spec: pd.DataFrame, pub: pd.DataFrame) -> Dates:
    data_start_date = max(spec.index)
    incomplete_start_date = data_start_date - dt.timedelta(days=INFER_DAYS)
    feature_start_date = incomplete_start_date - dt.timedelta(days=BACK_DAYS)
    predict_end_date = data_start_date + dt.timedelta(days=PRED_DAYS)
    publish_start_date = max(pub.index)
    publish_end_date = publish_start_date - dt.timedelta(days=PUB_DAYS)

    return Dates(
        data_start_date,
        incomplete_start_date,
        feature_start_date,
        predict_end_date,
        publish_start_date,
        publish_end_date
    )
