import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import datetime
import sys

with open("last_run.txt", "r") as f:
    d = f.read()
    print(d)
    print(datetime.date.today())
    if d == str(datetime.date.today()):
        print("Already done today")
        sys.exit(0)

START_DATE = datetime.datetime.strptime("2021-01-10", "%Y-%m-%d")

vaccines = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&metric=cumPeopleVaccinatedFirstDoseByPublishDate&metric=cumPeopleVaccinatedSecondDoseByPublishDate&metric=newPeopleVaccinatedFirstDoseByPublishDate&metric=newPeopleVaccinatedSecondDoseByPublishDate&format=csv")

vaccines = vaccines.drop(["areaCode", "areaType"], axis=1)
vaccines["date"] = pd.to_datetime(vaccines['date'])
vaccines.info()

tmp = vaccines.groupby("date").sum()
tmp["areaName"] = "total"
tmp = tmp.reset_index()

vaccines = vaccines.append(tmp)
vaccines = vaccines.set_index(["date", "areaName"])
vaccines["total_new"] = vaccines["newPeopleVaccinatedFirstDoseByPublishDate"] + vaccines["newPeopleVaccinatedSecondDoseByPublishDate"]

vaccine_totals = vaccines.xs("total", level=1)
mvg_avg = vaccines.rolling(7).sum()/7

fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)


plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["total_new"]].values.flatten(), fc=(.1, .2, 1, .3), label="Total Doses")
plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["newPeopleVaccinatedSecondDoseByPublishDate"]].values.flatten(), fc=(.2, .2, 1, 1), label="Second Doses")
plt.plot(mvg_avg.xs("total", level=1)[["total_new"]], color="orange", label="7 Day Moving Avg (Total Doses)", linewidth=3)
plt.plot(mvg_avg.xs("total", level=1)[["newPeopleVaccinatedSecondDoseByPublishDate"]], color="red", label="7 Day Moving Avg (2nd Dose)", linewidth=3)
plt.xlim(START_DATE, datetime.date.today())
# plt.hlines(1*10**6/7, START_DATE, datetime.date.today(), color="black", linestyle=":")
# plt.hlines(2*10**6/7, START_DATE, datetime.date.today(), color="black", linestyle=":")
plt.hlines(3*10**6/7, START_DATE, datetime.date.today(), color="black", linestyle=":", label="3 million /wk")
#plt.hlines(4*10**6/7, START_DATE, datetime.date.today(), color="black", linestyle=":")

plt.title(f"Vaccines by Publish Date ({datetime.date.today()})")
plt.legend()

plt.savefig("vaccines.png", pad_inches=0.05, transparent=False, dpi=600)

with open("last_run.txt", "w") as f:
    f.write(str(datetime.date.today()))
