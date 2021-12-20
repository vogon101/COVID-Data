# Update the archive
import cases.archive

## Clean the data
import cases.clean_data

## Train and run the model
import cases.train_model

from cases.predict import predict

cases.archive.update_archive()
cases.clean_data.clean_data()
models = cases.train_model.do_train_model()
predict(models)
