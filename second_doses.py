import matplotlib.pyplot as plt

from vaccines_data import *

wk_delays = [8, 10, 12]

fig = plt.figure(figsize=(15,10))
ax = fig.add_subplot(111)

for wk_delay in wk_delays:

    vts = vaccine_totals.copy()

    FUTURE_DATE = dt.date.today() + dt.timedelta(weeks=wk_delay)
    idx = pd.date_range(START_DATE, FUTURE_DATE, freq='D')

    expected_2nds = vts.shift(wk_delay * 7, "infer")

    vts = vts.reindex(idx)
    vts.loc[:, "E"] = expected_2nds.loc[:, "cumPeopleVaccinatedFirstDoseByPublishDate"]
    plt.plot(vts["E"], label=f"Cumulative First Doses {wk_delay} weeks injection", linestyle=":" if wk_delay != 12 else "-", lw=1 if wk_delay!=12 else 3)
plt.plot(vts["cumPeopleVaccinatedSecondDoseByPublishDate"], label="Cumulative Second Doses", lw=3)
plt.legend()
plt.title("Second Dose Progress by Publish Date")
plt.savefig("seconds.png", pad_inches=0.05, transparent=False, dpi=600)