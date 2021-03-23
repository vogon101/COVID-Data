import matplotlib.pyplot as plt

from vaccines_data import *


fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)
sax = ax.twinx()

wk_delay = 12
vts = vaccine_totals.copy()

FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=wk_delay)
idx = pd.date_range(START_DATE, FUTURE_DATE, freq='D')

expected_2nds = vts.shift(wk_delay * 7, "infer")

vts = vts.reindex(idx)
vts.loc[:, "E"] = expected_2nds.loc[:, "newPeopleVaccinatedFirstDoseByPublishDate"]
vts.loc[:, "cumE"] = expected_2nds.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]
dates = list(vts.index.values)
ax.bar(
    dates, vts["E"],
    label=f"Daily First Doses {wk_delay} weeks after injection",
    color="slategrey", alpha=0.5
)

sax.plot(vts["cumE"], linestyle="-", lw=3, color="darkslategrey", alpha=0.5, label=f"Cum. First Doses {wk_delay} weeks ago after injection")

ax.bar(dates, vts["newPeopleVaccinatedSecondDoseByPublishDate"], label="Daily Second Doses", lw=3, color="lightblue", alpha=0.8)
sax.plot(vts["cumPeopleVaccinatedSecondDoseByPublishDate"], label="Cumulative Second Doses", lw=3, color="darkblue")
plt.legend(loc=1)
ax.legend(loc=0)
plt.title("Second Dose Progress by Publish Date")
plt.savefig("seconds.png", pad_inches=0.05, transparent=False, dpi=600)
# plt.show()
