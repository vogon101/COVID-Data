from sklearn.linear_model import ARDRegression

INFER_DAYS = 5
PRED_DAYS = 7
BACK_DAYS = 30
PUB_DAYS = 30
TRAINING_DATA_PATH = "cases/trainingdata.csv"
ARCHIVE_PATH = "cases/data"
ARCHIVE_URL_SCHEME = \
    "https://api.coronavirus.data.gov.uk/v2/data?" \
    "areaType=overview&metric=newCasesBySpecimenDate&metric=newCasesBySpecimenDate&" \
    "metric=newCasesByPublishDate&format=csv&release={:4d}-{:02d}-{:02d}"
ARCHIVE_DELAY = 11

NORM_VALUE = 60700

MODEL_CONSTRUCTOR = lambda: ARDRegression()
