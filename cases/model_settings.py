INFER_DAYS = 5
PRED_DAYS = 5
BACK_DAYS = 30
TRAINING_DATA_PATH = "cases/trainingdata.csv"
ARCHIVE_PATH = "cases/data"
ARCHIVE_URL_SCHEME = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesBySpecimenDate&metric=newCasesBySpecimenDateChange&metric=newCasesBySpecimenDateRollingRate&metric=newCasesByPublishDateChangePercentage&format=csv&release={:4d}-{:02d}-{:02d}"