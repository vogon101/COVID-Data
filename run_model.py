# Update the archive
import cases.archive

## Clean the data
import cases.clean_data

## Train and run the model
import cases.train_model
from cases.CombiModel import CombiModel

from cases.predict import create_prediction

from cases.prediction_comparison import compare_predictions

cases.archive.update_archive()
cases.clean_data.clean_data()
model = CombiModel()
model = cases.train_model.do_train_model(model)
create_prediction(model)
compare_predictions()
