import pandas as pd

from cases.Dates import Dates


def get_features(latest_spec, latest_pub, dates: Dates):
    dow = dates.data_start_date.weekday()

    features_spec = select_features(latest_spec, dates.data_start_date, dates.feature_start_date)
    features_spec[f"{len(features_spec.columns)}"] = [dow]
    features_pubdate = select_features(latest_pub, dates.publish_start_date, dates.publish_end_date,
                                       offset=len(features_spec.columns))
    latest_features = features_spec.join(features_pubdate)
    return latest_features


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


def select_features(df, start, end, offset=0):
    df = df.loc[start: end].transpose().reset_index()
    df = df.drop(["index"], axis=1)
    df = df.rename(
        columns={x: (y + offset) for x, y in zip(df.columns, range(0, len(df.columns)))})
    return df