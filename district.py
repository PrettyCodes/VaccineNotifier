import os
import requests
import json
import time
from datetime import date, datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

host_email = "YOUR_EMAIL_ID"
host_email_pass = "YOUR_EMAIL_PASS"
receivers = "RECEIVERS_EMAIL_ID"

district_id = None
chk_no = 1
today = date.today().strftime("%d-%m-%Y")
my_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 RuxitSynthetic/1.0 v10138767079 t38550 ath9b965f92 altpub cvcv=2'}

def get_district():
    # Output the States
    states = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=my_headers).json()
    print('ID\tName')
    for state in states['states']:
        print(f"{state['state_id']}\t{state['state_name']}")

    state_id = input("Please enter the state id for your desired State: ")

    #Output the Districts based on the States selected
    districts = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/districts/"+state_id, headers=my_headers).json()
    print("")
    for district in districts['districts']:
        print(f"{district['district_id']}\t{district['district_name']}")

    district_id = input("Please enter the ID for your desired District: ")
    
    return district_id

def send_email(center, slots, date, vaccine):
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
                    table {{
                        margin-top: 20px;
                        margin-bottom: 20px;
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 12px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #FF80FF;
                        color: white;
                    }}
                    td, th {{
                        font-family: Verdana;
                        padding: 8px;
                        border: 1px solid gray;
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

    if("error" in district):
        print(district['error'])
        return

    for center in district['centers']:

        for session in center['sessions']:
            # Saving center details
            center_name = center['name']
            state = center['state_name']
            center_slots_dose1 = session['available_capacity_dose1']
            center_slots_dose2 = session['available_capacity_dose2']
            date = session['date']
            vaccine = session['vaccine']
            age = session['min_age_limit']
            
            if age == 18:
                # Vaccination center found for 18+
                if center_slots_dose1 > 0:
                    # Appointment slot found
                    print(str(center_slots_dose1)+' '+vaccine+' found at: ' +center_name+ ' for ' +date)

                    send_email(center_name, center_slots_dose1, date, vaccine)
                    break
                else:
                    print('No '+vaccine+' at: '+center_name+' for '+date)

#Start the program
while not district_id:
    district_id = int(get_district())
    
    if district_id not in range(1, 738):
        district_id = None
        print("\nIncorrect District ID, try again!\n")
        time.sleep(2)

while district_id:
    print(f"\n\nRunning check number: {chk_no}")

    try:
        print(f"\nChecking for District: {district_id}")
        jaipur1 = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id="+str(district_id)+"&date="+str(today), headers=my_headers).json()
        find_appointments(jaipur1)
    except:
        print("API Error, will try again!")
        time.sleep(5)
    finally:
        time.sleep(10)
        chk_no+=1