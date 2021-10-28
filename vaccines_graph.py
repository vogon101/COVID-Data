from matplotlib import pyplot as plt
import datetime
from vaccines_data import *

vmax = np.max(vaccines.xs("total", level=1)[["total_new"]].values.flatten()) * 1.075

fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)

plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["total_new"]].values.flatten(), fc=(0, .2, 1, .3), label="Total Doses")
plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["seconds_and_thirds"]].values.flatten(), fc=(.1, .2, 1, .7), label="Second Doses")
plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["newPeopleVaccinatedThirdInjectionByPublishDate"]].values.flatten(), fc=(.2, .2, 1, 1), label="Booster Doses")
plt.plot(mvg_avg.xs("total", level=1)[["total_new"]], color="orange", label="7 Day Moving Avg (Total Doses)", linewidth=3)
plt.plot(mvg_avg.xs("total", level=1)[["newPeopleVaccinatedSecondDoseByPublishDate"]], color="red", label="7 Day Moving Avg (2nd Dose)", linewidth=3)
plt.plot(mvg_avg.xs("total", level=1)[["newPeopleVaccinatedThirdInjectionByPublishDate"]], color="purple", label="7 Day Moving Avg (Booster Dose)", linewidth=3)
plt.xlim(START_DATE, datetime.date.today())

plt.hlines(4*10**6/7, START_DATE, datetime.date.today(), color="black", linestyle=":", label="4 million /wk")
plt.hlines(5*10**6/7, START_DATE, datetime.date.today(), color="grey", linestyle=":", label="5 million /wk")

plt.ylim(0, vmax)

d = MONDAY.date()
while d <= dt.date.today():
        plt.vlines([d], 0, vmax, color="grey", alpha=0.25)
        d += dt.timedelta(days=7)

plt.title(f"Vaccines by Publish Date ({datetime.date.today()})")
plt.legend()

plt.savefig("vaccines.png", pad_inches=0.05, transparent=False, dpi=600)


