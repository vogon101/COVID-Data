from matplotlib import pyplot as plt
import datetime
from vaccines_data import *


max_value = np.max(vaccines.xs("total", level=1)[["total_new"]].values.flatten()) * 1.075

print(vaccines["total_new"][-1])

def make_graph(start_date, monday, vmax):
        fig = plt.figure(figsize=(15,10))
        ax = fig.add_subplot(111)

        plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["total_new"]].values.flatten(), fc=(.2, .6, .2, .3), label="Total Doses")
        plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["seconds_and_thirds"]].values.flatten(), fc=(.7, .2, .2, .7), label="Second Doses")
        plt.bar(list(vaccine_totals.index.get_level_values("date")), height = vaccines.xs("total", level=1)[["newPeopleVaccinatedThirdInjectionByPublishDate"]].values.flatten(), fc=(.2, .2, .6, .8), label="Booster Doses")
        plt.plot(mvg_avg.xs("total", level=1)[["total_new"]], color="orange", label="7 Day Moving Avg (Total Doses)", linewidth=3)
        plt.plot(mvg_avg.xs("total", level=1)[["newPeopleVaccinatedSecondDoseByPublishDate"]], color="red", label="7 Day Moving Avg (2nd Dose)", linewidth=3)
        plt.plot(mvg_avg.xs("total", level=1)[["newPeopleVaccinatedThirdInjectionByPublishDate"]], color=(.2, .2, 1, 1), label="7 Day Moving Avg (Booster Dose)", linewidth=3)
        plt.xlim(start_date, datetime.date.today())

        plt.hlines(4*10**6/7, start_date, datetime.date.today(), color="black", linestyle=":", label="4 million /wk")
        plt.hlines(5*10**6/7, start_date, datetime.date.today(), color="grey", linestyle=":", label="5 million /wk")
        plt.hlines(1e6, start_date, datetime.date.today(), color="green", linestyle=":", label="1 million /day")

        plt.ylim(0, vmax)

        d = monday.date()
        while d <= dt.date.today():
                plt.vlines([d], 0, vmax, color="grey", alpha=0.25)
                d += dt.timedelta(days=7)


make_graph(START_DATE, MONDAY, max_value)

plt.title(f"Vaccines by Publish Date ({datetime.date.today()})")
plt.legend()

plt.savefig("vaccines.png", pad_inches=0.05, transparent=False, dpi=600)


make_graph(START_DATE + datetime.timedelta(days=30*7), MONDAY+ datetime.timedelta(days=30*7), 1.1e6)

plt.title(f"Vaccines by Publish Date ({datetime.date.today()})")
plt.legend()

plt.savefig("out/vaccines_less.png", pad_inches=0.05, transparent=False, dpi=600)

