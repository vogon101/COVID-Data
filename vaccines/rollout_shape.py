import matplotlib.pyplot as plt
from vaccines_data import *

print("Rollout Shape Graph")

SHIFT_TO = 5e6
vts = vaccine_totals.copy()

i, j = 0, 0
gaps_2nd3rd, gaps_1st3rd = [], []


def get_offset(key):
    for date in vts.index:
        if vts.loc[date, key] > SHIFT_TO:
            print(date)
            return date


date3 = get_offset("cumPeopleVaccinatedThirdInjectionByPublishDate")
date2 = get_offset("cumPeopleVaccinatedSecondDoseByPublishDate")
date1 = get_offset("cumPeopleVaccinatedFirstDoseByPublishDate")

shift_2 = -((date2 - date3).total_seconds() / (60 * 60 * 24 * 7))
shift_1 = -((date1 - date3).total_seconds() / (60 * 60 * 24 * 7))
print(f"Shifting second doses by {shift_2:.2f} weeks")
print(f"Shifting second doses by {shift_1:.2f} weeks")

offset = 7*10

FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=shift_2)
idx = pd.date_range(START_DATE, FUTURE_DATE, freq='1D')


vts = vts.reindex(index=idx)
expected_2nds = vts.shift(shift_2 * 7, "infer")
expected_1sts = vts.shift(shift_1 * 7, "infer")

vts.loc[:, "cumE_3"] = expected_2nds.loc[:, "cumPeopleVaccinatedSecondDoseByPublishDate"]
vts.loc[:, "cumE_2"] = expected_1sts.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]

start_date = dt.date.today() - dt.timedelta(days=int(26 * 7))
end_date = dt.date.today() + dt.timedelta(days=int(shift_2 * 7 + 2))

fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)

plt.hlines(SHIFT_TO, start_date, end_date, color="grey", linestyle=":")
plt.axvline(date3, color="grey", linestyle=":")

ax.plot(vts["cumE_2"], linestyle="-", lw=3, color="red", alpha=0.75,
         label=f"Cum. First Doses  (Shifted {shift_1:.2f} weeks)")
ax.plot(vts["cumE_3"], linestyle="-", lw=3, color="green", alpha=0.75,
         label=f"Cum. Second Doses (Shifted {shift_2:.2f} weeks)")

ax.plot(vts["cumPeopleVaccinatedThirdInjectionByPublishDate"], label="Cumulative Third Doses", lw=3,
        color="darkblue", alpha=0.75)

ax.set_xlabel("Date")
ax.set_ylabel("Doses (10,000,000)")

plt.xlim(start_date, end_date)

title_string = "Vaccine Rollout by Dose"
subtitle_string = f"Aligned to point of {int(SHIFT_TO / 1e6):d} million doses delivered."

# plt.title("Vaccine Rollout by Dose")
plt.suptitle(title_string, y=0.95, fontsize=18)
plt.title(subtitle_string, fontsize=10)

plt.legend(loc=0)
# ax.legend(loc=1)
plt.savefig("out/rollout.png", pad_inches=0.05, transparent=False, dpi=600)
