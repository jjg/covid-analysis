import smtplib
import pandas as pd

from config import config

from email.message import EmailMessage

q = "https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.csv?where=GEO%20%3D%20%27County%27&outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D"
ds = pd.read_csv(q)

# TODO: Externalize this into a dictionary of counties/pops/emails in the config
county = "Dodge"
county_population = 90005

# TODO: Loop over configured counties
dc = ds[ds.NAME == county]

dc_summary = dc[["DATE", "NEGATIVE", "POSITIVE", "DEATHS", "DTH_NEW", "HOSP_YES", "POS_NEW"]].sort_values(["DATE"], ascending=False).head(20)

# Reverse the sort
dc_summary = dc_summary.sort_values(["DATE"], ascending=True)

# Add a calculated column for the "new cases per 100k of population" from the Harvard model
dc_summary["pos_new_rolling"] = dc_summary["POS_NEW"].rolling(7).mean()
dc_summary["new_per_100k"] = (dc_summary["pos_new_rolling"] / county_population) * 100000

# Grab last week and sort
dc_summary = dc_summary.tail(7).sort_values(["DATE"], ascending=False)

todays_data = f"""

date: {dc_summary.iloc[0]['DATE']}
total positives: {dc_summary.iloc[0]['POSITIVE']}
total hospitalizations: {dc_summary.iloc[0]['HOSP_YES']}
total deaths: {dc_summary.iloc[0]['DEATHS']}
new positives: {dc_summary.iloc[0]['POS_NEW']}
new deaths: {dc_summary.iloc[0]['DTH_NEW']}
rolling new positives (7 day avg): {dc_summary.iloc[0]['pos_new_rolling']}
rolling new positives per 100k (7 day avg): {dc_summary.iloc[0]['new_per_100k']}

"""

message = EmailMessage()
message["Subject"] = "COVID-19 Update"

# TODO: Send to recipients configured for the selected county
message["From"] = config["from"]
message["To"] = config["to"]
message.set_content(todays_data)

# send email
smtp = smtplib.SMTP(f"{config['smtp_server']}:{config['smtp_port']}")
smtp.ehlo()
smtp.starttls()
smtp.login(config["from"], config["password"])
smtp.send_message(message)
smtp.quit()


