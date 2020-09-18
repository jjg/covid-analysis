import pandas as pd

q = "https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.csv?where=GEO%20%3D%20%27County%27&outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D"
ds = pd.read_csv(q)

county = "Dodge"
county_population = 90005

dc = ds[ds.NAME == county]

dc_summary = dc[["DATE", "NEGATIVE", "POSITIVE", "DEATHS", "DTH_NEW", "HOSP_YES", "POS_NEW", "TEST_NEW" ]].sort_values(["DATE"], ascending=False)

dc_summary["rolling_positive"] = (dc_summary["POSITIVE"]/(dc_summary["POSITIVE"] + dc_summary["NEGATIVE"])) * 100

# TODO: To match the model, this should be a 7 day moving average
dc_summary["new_per_100k"] = (dc_summary["POS_NEW"] / county_population) * 100000

print(f"total positives: {dc_summary.iloc[0]['POSITIVE']}")
print(f"total deaths: {dc_summary.iloc[0]['DEATHS']}")
print(f"new positives: {dc_summary.iloc[0]['POS_NEW']}")
print(f"rolling positives: {dc_summary.iloc[0]['rolling_positive']}")
print(f"new positives per 100k: {dc_summary.iloc[0]['new_per_100k']}")
print(f"total hospitalizations: {dc_summary.iloc[0]['HOSP_YES']}")



