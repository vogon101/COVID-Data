from vaccines_data import *

from matplotlib import pyplot as plt

vts = vaccine_totals.copy()

print(vts)
print(vts.index)
i = 0
dates = []
gaps = []
for date in vts.index:
    print("_-------------------")
    print(vts.iloc[i]["cumPeopleVaccinatedFirstDoseByPublishDate"])
    while vts.loc[date, "cumPeopleVaccinatedSecondDoseByPublishDate"] > vts.iloc[i]["cumPeopleVaccinatedFirstDoseByPublishDate"]:
        i+= 1
    dates.append((date, vts.index[i]))
    gaps.append((date - vts.index[i]).total_seconds() / (60 * 60 * 24 * 7))

offset = 7*10
plt.plot(vts.index[offset:], gaps[offset:])
plt.show()