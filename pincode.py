import os
import requests
import time
import json
from datetime import date, datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Enter the below details before starting
pin_code = "PIN_CODE"
host_email = "YOUR_EMAIL_ID"
host_email_pass = "YOUR_EMAIL_PASS"
receivers = "RECEIVERS_EMAIL_ID"

chk_no = 1
today = date.today().strftime("%d-%m-%Y")
my_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 RuxitSynthetic/1.0 v10138767079 t38550 ath9b965f92 altpub cvcv=2'}

def send_email(center, slots, date, receivers, vaccine):
    # Setting up the email
    message = MIMEMultipart("alternative")
    message["From"] = host_email
    message["To"] = receivers
    message["Subject"] = "CoWin - Found vaccine appointment for "+vaccine
    
    html =f"""\
            <!DOCTYPE html>
            <head>
                <style>
                    body{{
                        font-weight: normal;
                    }}
                    h2{{
                        font-family: Verdana;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                    p{{
                        line-height: 18px;
                        font-family: Verdana;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <html>
                <body>
                    <p>Hi,</p>
                    <h2>Found COVID Vaccine appointment on cowin.gov.in</h2>
                    <p>Center: {center} with {slots} available slot/s for date {date}.<br></p>
                </body>
            </html>
            """
    body = MIMEText(html, "html")
    message.attach(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        print("Sending email now")
        smtp.login(host_email, host_email_pass)
        smtp.send_message(message)

def find_appointments(district):
    
    for center in district['centers']:
        for session in center['sessions']:

            age = session['min_age_limit']
            if age == 18:
                # Vaccination center found for 18+
                center_name = center['name']

                # Highly unlikey you will need this for dose 2
                # If you do, change the below to 'available_capacity_dose2'
                no_of_slots = session['available_capacity_dose1']
                date = session['date']
                vaccine = session['vaccine']

                if no_of_slots > 0:
                    # Appointment slot found
                    print(str(no_of_slots)+' appointments found at: ' +center_name+ ' for ' +date)
                    send_email(center_name, no_of_slots, date, receivers, vaccine)
                    break
                else:
                    print('No '+vaccine+' at: '+center_name+' for '+date)

while True:
    print("\nRunning check number: "+str(chk_no))

    try:
        print("\nChecking for Pincode: "+pin_code)
        centers = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode="+pin_code+"&date="+str(today), headers=my_headers).json()
        find_appointments(centers)
    except:
        print("API Error, will try again!")
        time.sleep(5)
    else:
        time.sleep(10) # If rush time, decrease this. If chill time, increase this.
        chk_no+=1