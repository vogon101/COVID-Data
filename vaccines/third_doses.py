import matplotlib.pyplot as plt
from vaccines_data import *

vts = vaccine_totals.copy()

i, j = 0, 0
dates_2nd3rd, dates_1st3rd = [], []
gaps_2nd3rd, gaps_1st3rd = [], []
for date in vts.index:
    if vts.loc[date, "cumPeopleVaccinatedThirdInjectionByPublishDate"] <= 0:
        continue
    while vts.loc[date, "cumPeopleVaccinatedThirdInjectionByPublishDate"] > vts.iloc[i]["cumPeopleVaccinatedSecondDoseByPublishDate"]:
        i += 1

    while vts.loc[date, "cumPeopleVaccinatedThirdInjectionByPublishDate"] > vts.iloc[j]["cumPeopleVaccinatedFirstDoseByPublishDate"]:
        j += 1

    dates_2nd3rd.append(vts.index[i])
    gaps_2nd3rd.append((date - vts.index[i]).total_seconds() / (60 * 60 * 24 * 7))

    dates_1st3rd.append(vts.index[j])
    gaps_1st3rd.append((date - vts.index[j]).total_seconds() / (60 * 60 * 24 * 7))

offset = 7*10

wk_delay_2nd3rd = gaps_2nd3rd[-1]
wk_delay_1st3rd = gaps_1st3rd[-1]

FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=wk_delay_2nd3rd)
idx = pd.date_range(START_DATE, FUTURE_DATE, freq='1D')

gaps_df_2nd3rd = pd.DataFrame({"date": dates_2nd3rd, "gaps": gaps_2nd3rd})\
    .reset_index()\
    .drop_duplicates(subset="date", keep="last")\
    .set_index("date")\
    .shift(periods=wk_delay_2nd3rd * 7, freq="D")

gaps_df_1st3rd = pd.DataFrame({"date": dates_1st3rd, "gaps": gaps_1st3rd})\
    .reset_index()\
    .drop_duplicates(subset="date", keep="last")\
    .set_index("date")\
    .shift(periods=wk_delay_1st3rd * 7, freq="D")


vts = vts.reindex(index=idx)
expected_2nds = vts.shift(wk_delay_2nd3rd * 7, "infer")
expected_1sts = vts.shift(wk_delay_1st3rd * 7, "infer")

vts.loc[:, "cumE_3"] = expected_2nds.loc[:, "cumPeopleVaccinatedSecondDoseByPublishDate"]
vts.loc[:, "cumE_2"] = expected_1sts.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]

vts = pd.concat([vts, gaps_df_2nd3rd], axis=1)


fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)
# sax = ax.twinx()

ax.plot(vts["cumE_2"], linestyle="-", lw=3, color="red", alpha=0.5,
         label=f"Cum. First Doses {wk_delay_1st3rd:.2f} weeks ago after injection")
ax.plot(vts["cumE_3"], linestyle="-", lw=3, color="green", alpha=0.5,
         label=f"Cum. Second Doses {wk_delay_2nd3rd:.2f} weeks ago after injection")

ax.plot(vts["cumPeopleVaccinatedThirdInjectionByPublishDate"], label="Cumulative Third Doses", lw=3, color="darkblue")

# ax.plot(gaps_df_2nd3rd["gaps"], label="Effective Gap (2nd to 3rd)", color="green")
# ax.plot(gaps_df_1st3rd["gaps"], label="Effective Gap (1st to 3rd)", color="red")

# ax.set_ylim(min(gaps_2nd3rd[offset:]) - 5, max(gaps_1st3rd) + 2)
# ax.set_ylabel("Gap (Weeks)")
ax.set_xlabel("Date")
ax.set_ylabel("Doses (10,000,000)")

plt.xlim(dt.date.today() - dt.timedelta(days=int(26 * 7)), dt.date.today() + dt.timedelta(days=int(wk_delay_2nd3rd * 7 + 2)))

plt.title("Booster Dose Progress by Publish Date")

plt.legend(loc=0)
# ax.legend(loc=1)
plt.savefig("out/thirds.png", pad_inches=0.05, transparent=False, dpi=600)
