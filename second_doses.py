import matplotlib.pyplot as plt

from vaccines_data import *


fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)
sax = ax.twinx()


vts = vaccine_totals.copy()

i = 0
dates = []
gaps = []
for date in vts.index:
    while vts.loc[date, "cumPeopleVaccinatedSecondDoseByPublishDate"] > vts.iloc[i]["cumPeopleVaccinatedFirstDoseByPublishDate"]:
        i+= 1
    dates.append(vts.index[i])
    gaps.append((date - vts.index[i]).total_seconds() / (60 * 60 * 24 * 7))

offset = 7*10

wk_delay = gaps[-1]

FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=wk_delay)
idx = pd.date_range(START_DATE, FUTURE_DATE, freq='1D')

gaps_df = pd.DataFrame({"date": dates, "gaps": gaps})\
    .reset_index()\
    .drop_duplicates(subset="date", keep="last")\
    .set_index("date")\
    .shift(periods=wk_delay*7, freq="D")

vts = vts.reindex(index=idx)
expected_2nds = vts.shift(wk_delay * 7, "infer")


vts.loc[:, "E"] = expected_2nds.loc[:, "newPeopleVaccinatedFirstDoseByPublishDate"]
vts.loc[:, "cumE"] = expected_2nds.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]
vts.info()
vts = pd.concat([vts, gaps_df], axis=1)

sax.plot(vts["cumE"], linestyle="-", lw=3, color="darkslategrey", alpha=0.5,
         label=f"Cum. First Doses {wk_delay:.2f} weeks ago after injection")
ax.plot(gaps_df["gaps"], label="Effective")
ax.set_ylim(min(gaps[offset:]) - 0.5, max(gaps) + 0.5)

sax.plot(vts["cumPeopleVaccinatedSecondDoseByPublishDate"], label="Cumulative Second Doses", lw=3, color="darkblue")
plt.legend(loc=1)
ax.legend(loc=0)
plt.title("Second Dose Progress by Publish Date")
plt.savefig("seconds.png", pad_inches=0.05, transparent=False, dpi=600)
