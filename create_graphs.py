import datetime, time
import sys
import pandas as pd


with open("last_run.txt", "r+") as f:
    d = f.read()
    f.seek(0)
    print(d)
    print(int(time.time()))
    vaccines = None
    if int(d) > int(time.time()) - 60 * 5:
        print("Using cached file")
        vaccines = pd.read_csv("latest.csv")
    else:
        print("Fecthing new data")

        vaccines = pd.read_csv(
        "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=cumPeopleVaccinatedFirstDoseByPublishDate&metric=cumPeopleVaccinatedSecondDoseByPublishDate&metric=newPeopleVaccinatedFirstDoseByPublishDate&metric=newPeopleVaccinatedSecondDoseByPublishDate&format=csv"
                        )

        vaccines_thirds = pd.read_csv(
            "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=cumPeopleVaccinatedThirdInjectionByPublishDate&metric=newPeopleVaccinatedThirdInjectionByPublishDate&metric=cumPeopleVaccinatedFirstDoseByPublishDate&format=csv"
        )

        vaccines_demos = pd.read_csv(
            "https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&metric=vaccinationsAgeDemographics&format=csv"
        )

        vaccines["cumPeopleVaccinatedThirdInjectionByPublishDate"] = vaccines_thirds["cumPeopleVaccinatedThirdInjectionByPublishDate"]
        vaccines["newPeopleVaccinatedThirdInjectionByPublishDate"] = vaccines_thirds["newPeopleVaccinatedThirdInjectionByPublishDate"]

        vaccines.info()
        vaccines_demos.info()

        vaccines.to_csv("latest.csv")
        vaccines_demos.to_csv("demos.csv")
        f.write(str(int(time.time())))
        f.truncate()



    import vaccines.vaccines_graph
    import vaccines.second_doses
    import vaccines.third_doses
    import vaccines.rollout_shape
    import vaccines.demographics




    print("Complete")
