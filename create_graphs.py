import datetime
import sys
import pandas as pd

with open("last_run.txt", "r") as f:
    d = f.read()
    print(d)
    print(datetime.date.today())
    if d == str(datetime.date.today()):
        print("Already done today")
        sys.exit(0)

vaccines = pd.read_csv(
    "https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&metric=cumPeopleVaccinatedFirstDoseByPublishDate&metric=cumPeopleVaccinatedSecondDoseByPublishDate&metric=newPeopleVaccinatedFirstDoseByPublishDate&metric=newPeopleVaccinatedSecondDoseByPublishDate&format=csv"
)

vaccines.to_csv("latest.csv")

import vaccines_graph
import second_doses

with open("last_run.txt", "w") as f:
    f.write(str(datetime.date.today()))

print("Complete")