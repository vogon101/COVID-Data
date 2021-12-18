import matplotlib.pyplot as plt

from vaccines_data import *


fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)
sax = ax.twinx()


vts = vaccine_totals.copy()

i, j = 0, 0
dates_thirds, dates_seconds = [], []
gaps_thirds, gaps_seconds = [], []
for date in vts.index:
    while vts.loc[date, "cumPeopleVaccinatedThirdInjectionByPublishDate"] > vts.iloc[i]["cumPeopleVaccinatedSecondDoseByPublishDate"]:
        i+= 1

    while vts.loc[date, "cumPeopleVaccinatedThirdInjectionByPublishDate"] > vts.iloc[j]["cumPeopleVaccinatedFirstDoseByPublishDate"]:
        j += 1

    dates_thirds.append(vts.index[i])
    gaps_thirds.append((date - vts.index[i]).total_seconds() / (60 * 60 * 24 * 7))

    dates_seconds.append(vts.index[j])
    gaps_seconds.append((date - vts.index[j]).total_seconds() / (60 * 60 * 24 * 7))

offset = 7*10

wk_delay_thirds = gaps_thirds[-1]
wk_delay_seconds = gaps_seconds[-1]

FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=wk_delay_thirds)
idx = pd.date_range(START_DATE, FUTURE_DATE, freq='1D')

gaps_df_3rds = pd.DataFrame({"date": dates_thirds, "gaps": gaps_thirds})\
    .reset_index()\
    .drop_duplicates(subset="date", keep="last")\
    .set_index("date")\
    .shift(periods=wk_delay_thirds * 7, freq="D")

vts = vts.reindex(index=idx)
expected_3rds = vts.shift(wk_delay_thirds * 7, "infer")
expected_2nds = vts.shift(wk_delay_seconds * 7, "infer")


vts.loc[:, "cumE_3"] = expected_3rds.loc[:, "cumPeopleVaccinatedSecondDoseByPublishDate"]
vts.loc[:, "cumE_2"] = expected_2nds.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]
vts.info()
vts = pd.concat([vts, gaps_df_3rds], axis=1)

sax.plot(vts["cumE_2"], linestyle="-", lw=3, color="red", alpha=0.5,
         label=f"Cum. First Doses {wk_delay_thirds:.2f} weeks ago after injection")
sax.plot(vts["cumE_3"], linestyle="-", lw=3, color="green", alpha=0.5,
         label=f"Cum. Second Doses {wk_delay_seconds:.2f} weeks ago after injection")
ax.plot(gaps_df_3rds["gaps"], label="Effective Gap")
ax.set_ylim(min(gaps_thirds[offset:]) - 0.5, max(gaps_thirds) + 0.5)

sax.plot(vts["cumPeopleVaccinatedThirdInjectionByPublishDate"], label="Cumulative Third Doses", lw=3, color="darkblue")


plt.xlim(dt.date.today() - dt.timedelta(days=int(26 * 7)), dt.date.today() + dt.timedelta(days=int(wk_delay_thirds * 7 + 2)))

plt.title("Booster Dose Progress by Publish Date")


plt.legend(loc=0)
ax.legend(loc=1)
plt.savefig("out/thirds.png", pad_inches=0.05, transparent=False, dpi=600)
