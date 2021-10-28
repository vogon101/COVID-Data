import datetime as dt
import pandas as pd
import numpy as np

START_DATE = dt.datetime.strptime("2021-01-10", "%Y-%m-%d")
MONDAY = dt.datetime.strptime("2021-01-11", "%Y-%m-%d")

vaccines = pd.read_csv("latest.csv")

vaccines = vaccines.drop(["areaCode", "areaType"], axis=1)
vaccines["date"] = pd.to_datetime(vaccines['date'])
vaccines.info()

tmp = vaccines.groupby("date").sum()
tmp["areaName"] = "total"
tmp = tmp.reset_index()

vaccines = vaccines.append(tmp)
vaccines = vaccines.set_index(["date", "areaName"])
vaccines["total_new"] = vaccines["newPeopleVaccinatedFirstDoseByPublishDate"] + vaccines["newPeopleVaccinatedSecondDoseByPublishDate"] + vaccines["newPeopleVaccinatedThirdInjectionByPublishDate"]
vaccines["seconds_and_thirds"] = vaccines["newPeopleVaccinatedSecondDoseByPublishDate"] + vaccines["newPeopleVaccinatedThirdInjectionByPublishDate"]

vaccine_totals = vaccines.xs("total", level=1).copy()
mvg_avg = vaccines.rolling(7).sum()/7

