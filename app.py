from flask import Flask, render_template, request
import requests
import json
import yagmail
import datetime
import time
import smtplib, ssl

app = Flask(__name__)


@app.route('/')
def index(user_list):
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
            url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}'
            response = requests.get(url.format(user['pin'], datetime.date.today().strftime('%d-%m-%Y')),
                                    headers=headers)
            data = json.loads(response.text)
            availability = []
            if len(data['centers']) > 0:
                for center in data['centers']:
                    temp_sessions = []
                    for session in center['sessions']:
                        if session['available_capacity'] > 0 and session['min_age_limit'] == 45:
                            temp_sessions.append(session)
                    temp_center = center
                    if len(temp_sessions) > 0:
                        temp_center['sessions'] = temp_sessions
                        availability.append(temp_center)
        except Exception as E:
            raise E
        if availability:
            email_data.append({'email': user['email'], 'info': availability})
    send_mail_using_gmail(email_data)
    # return render_template('index.html', caseData=data['statewise'])


def send_mail_using_gmail(email_data):
    with open('settings.json', 'r') as file:
        secret = json.loads(file.read().replace('\n', ''))

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "xylotronjay@gmail.com"  # Enter your address
    password = secret['gmail_password']

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        for receiver in email_data:
            receiver_email = receiver['email']
            message = """\
                Subject: Test

                Hi! Following center(s) & slot(s) are available for you:"""
            count = 1
            for center in receiver['info']:
                text = str(count + 1) + '. '
                pass

            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


if __name__ == '__main__':
    # app.run(debug=True)
    input_dict = {
        "user_list": [
            {"email": "achal2812@gmail.com", "pin": "110085"},
            {"email": "jso101196@gmail.com", "pin": "110045"}]
    }
    index(input_dict['user_list'])
