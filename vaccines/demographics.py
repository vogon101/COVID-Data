import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from vaccines_data import *

plt.clf()
print("Demographic Graphs")

columns = {
    "12_15": ["12_15"],
    "16_17": ["16_17"],
    "18_29": ["18_24", "25_29"],
    "30_39": ["30_34", "35_39"],
    "40_49": ["40_44", "45_49"],
    "50_59": ["50_54", "55_59"],
    "60_69": ["60_64", "65_69"],
    "70_79": ["70_74", "75_79"],
    "80_89": ["80_84", "85_89"],
    "90+"  : ["90+"]
}

colors = [
    "firebrick", "orangered", "darkorange", "olive", "mediumseagreen", "teal", "steelblue", "mediumpurple",
    "deeppink", "slategrey",
]

shift_2 = 28.86
shift_1 = 39.0


def make_graph(start_date, vds, METRIC, alpha=1.0, label=True, linestyle="-"):
    print(f"Demographic graph for {METRIC}")
    vds = vds[["date", "age", "areaName", METRIC]]
    vds = vds.set_index(["date", "age", "areaName"])\
                         .sort_index().loc[start_date:, :, "England"].droplevel(2).sort_index()

    vds = vds.unstack(level=1, fill_value=0)

    for k, v in columns.items():
        if len(v) == 1:
            continue

        vds = vds.join(
            vds[(METRIC, v[0])]
                .add(vds[(METRIC, v[1])]).div(2)
                .to_frame()
                .rename(columns={0: (METRIC, k)})[[(METRIC, k)]]
        )


    vds = vds[[(METRIC, k) for k in columns.keys()]]

    for i, col in enumerate(vds.columns):
        plt.plot(vds[col], label=col[1] if label else None, alpha=alpha, color=colors[i], lw=3, linestyle=linestyle)

    plt.ylim(0, 100)
    plt.legend()

make_graph(
    dt.date(2021, 9, 15),
    vaccines_demos.copy(),
    "cumVaccinationThirdInjectionUptakeByVaccinationDatePercentage"
)

make_graph(
    dt.date(2021, 9, 15),
    vaccines_demos.copy(),
    "cumVaccinationSecondDoseUptakeByVaccinationDatePercentage",
    alpha=0.3, label=False, linestyle=":"
)

plt.title("Booster/3rd Dose Rollout By Age")
plt.savefig("out/demographics_3.png", pad_inches=0.05, transparent=False, dpi=300)
plt.clf()

make_graph(
    "2020-12-01",
    vaccines_demos.copy(),
    "cumVaccinationSecondDoseUptakeByVaccinationDatePercentage"
)


make_graph(
    dt.date(2020, 12, 1),
    vaccines_demos.copy(),
    "cumVaccinationFirstDoseUptakeByVaccinationDatePercentage",
    alpha=0.3, label=False, linestyle=":"
)
plt.title("2nd Dose Rollout By Age")
plt.savefig("out/demographics_2.png", pad_inches=0.05, transparent=False, dpi=300)
plt.clf()

make_graph(
    "2020-11-01",
    vaccines_demos.copy(),
    "cumVaccinationFirstDoseUptakeByVaccinationDatePercentage"
)

plt.title("1st Dose Rollout By Age")
plt.savefig("out/demographics_1.png", pad_inches=0.05, transparent=False, dpi=300)
plt.clf()