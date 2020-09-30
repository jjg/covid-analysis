import sys
import smtplib
import pandas as pd

from config import config

from email.message import EmailMessage

def download_data():
    q = "https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.csv?where=GEO%20%3D%20%27County%27&outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D"
    return pd.read_csv(q)

def process_data(ds):
    # TODO: Externalize this into a dictionary of counties/pops/emails in the config
    county = "Dodge"
    county_population = 90005

    dc = ds[ds.NAME == county]

    dc_summary = dc[["DATE", "NEGATIVE", "POSITIVE", "DEATHS", "DTH_NEW", "HOSP_YES", "POS_NEW"]].sort_values(["DATE"], ascending=False).head(20)

    # Reverse the sort
    dc_summary = dc_summary.sort_values(["DATE"], ascending=True)

    dc_summary["rolling_positive"] = (dc_summary["POSITIVE"]/(dc_summary["POSITIVE"] + dc_summary["NEGATIVE"])) * 100

    # Add a calculated column for the "new cases per 100k of population" from the Harvard model
    dc_summary["pos_new_rolling"] = dc_summary["POS_NEW"].rolling(7).mean()
    dc_summary["new_per_100k"] = (dc_summary["pos_new_rolling"] / county_population) * 100000

    # Grab last week and sort
    dc_summary = dc_summary.tail(7).sort_values(["DATE"], ascending=False)

    return dc_summary

def data_summary_message(dc_summary):
    return f"""

    date: {dc_summary.iloc[0]['DATE']}
    total positives: {dc_summary.iloc[0]['POSITIVE']}
    rolling percent positive: {dc_summary.iloc[0]['rolling_positive']}
    total hospitalizations: {dc_summary.iloc[0]['HOSP_YES']}
    total deaths: {dc_summary.iloc[0]['DEATHS']}
    new positives: {dc_summary.iloc[0]['POS_NEW']}
    new deaths: {dc_summary.iloc[0]['DTH_NEW']}
    rolling new positives (7 day avg): {dc_summary.iloc[0]['pos_new_rolling']}
    rolling new positives per 100k (7 day avg): {dc_summary.iloc[0]['new_per_100k']}

    """

def error_message():
    return f"""

    No new data was provided by DHS. 

    """

    return error_message

def send_email(message_text):
    message = EmailMessage()
    message["Subject"] = "COVID-19 Update"

    message["From"] = config["from"]
    message["To"] = config["to"]
    message.set_content(message_text)

    # send email
    smtp = smtplib.SMTP(f"{config['smtp_server']}:{config['smtp_port']}")
    smtp.ehlo()
    smtp.starttls()
    smtp.login(config["from"], config["password"])
    smtp.send_message(message)
    smtp.quit()

# now...get busy!
try:
    ds = download_data()

    if len(ds) > 0:
        send_email(data_summary_message(process_data(ds)))

        #processed_data = process_data(ds)
        #email_message = data_summary_email(processed_data)
        #send_email(email_message)
    else:
        send_email(error_message())
except:
    send_email(f"Awww shit dawg! {sys.exc_info()[0]}")
