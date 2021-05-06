import datetime
import json
import smtplib
import ssl
import time
import requests
from flask import Flask, request, render_template

app = Flask(__name__)
user_list = [{"email": "achal2812@gmail.com", "districts": ['143', '146']},
             {"email": "vicky30498@gmail.com", "districts": ['143', '146']}]

district_reference = [
    {
        "district_id": 140,
        "district_name": "New Delhi"
    },
    {
        "district_id": 141,
        "district_name": "Central Delhi"
    },
    {
        "district_id": 142,
        "district_name": "West Delhi"
    },
    {
        "district_id": 143,
        "district_name": "North West Delhi"
    },
    {
        "district_id": 144,
        "district_name": "South East Delhi"
    },
    {
        "district_id": 145,
        "district_name": "East Delhi"
    },

    {
        "district_id": 146,
        "district_name": "North Delhi"
    },
    {
        "district_id": 147,
        "district_name": "North East Delhi"
    },

    {
        "district_id": 148,
        "district_name": "Shahdara"
    },
    {
        "district_id": 149,
        "district_name": "South Delhi"
    },

    {
        "district_id": 150,
        "district_name": "South West Delhi"
    },

]


@app.route('/done', methods=['GET', 'POST'])
def api():
    if request.method == 'POST':
        user_list.append({"email": request.form['mail'], "districts": request.form['districts']})
        return render_template('landing.html')
    yield
    parse()


@app.route('/')
def home():
    return render_template('index.html')


def parse():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "cdn-api.co-vin.in",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    email_data = []
    for user in user_list:
        try:
            url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}'
            availability = []
            for district in user['districts']:
                response = requests.get(url.format(str(district), datetime.date.today().strftime('%d-%m-%Y')), headers=headers)
                data = json.loads(response.text)
                if len(data['centers']) > 0:
                    for center in data['centers']:
                        temp_sessions = []
                        for session in center['sessions']:
                            if session['available_capacity'] > 0 and session['min_age_limit'] < 45:
                                temp_sessions.append(session)
                        temp_center = center
                        if len(temp_sessions) > 0:
                            temp_center['sessions'] = temp_sessions
                            availability.append(temp_center)
        except Exception as E:
            raise E
        if availability:
            email_data.append({'email': user['email'], 'info': availability})
    if email_data:
        send_mail_using_gmail(email_data)
    time.sleep(120)
    parse()


def send_mail_using_gmail(email_data):
    with open('settings.json', 'r') as file:
        secret = json.loads(file.read().replace('\n', ''))

    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "xylotronjay@gmail.com"
    password = secret['gmail_password']

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        for receiver in email_data:
            receiver_email = receiver['email']
            message = """Subject: CoWIN: New Slots Available\nFrom: CoWIN Slot Notifier\n
            \nThis is an auto-generated mail, please do not reply.
            \n\nHi! Following center(s) are available for you:""".format(sender_email, receiver_email)
            count = 1
            for center in receiver['info']:
                primary_text = ('\n\n' + str(count) + '. {0}, {1}, {2}, {3}, {4}').format(center['name'], center['address'], center['state_name'], center['district_name'],
                                                                                          center['pincode'])
                secondary_text = ''
                for avail_date in center['sessions']:
                    secondary_text = (secondary_text + '\n\tDate: {0}, Vaccine: {1}, Capacity: {2}').format(
                        avail_date['date'], avail_date['vaccine'], str(avail_date['available_capacity']), str(avail_date['slots']))
                message = message + primary_text + secondary_text
                count += 1
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


if __name__ == '__main__':
    parse()
