#!/usr/bin/env python

import datetime
import json
import os
import requests

API_URL = "https://api.pushover.net/1"

ENDPOINT_LOGIN = "{api_url}/users/login.json".format(api_url=API_URL)
ENDPOINT_DEVICES = "{api_url}/devices.json".format(api_url=API_URL)
ENDPOINT_MESSAGES = "{api_url}/messages.json".format(api_url=API_URL)
ENDPOINT_UPDATE_HIGHEST_MESSAGE = \
        "{api_url}/devices/{device_id}/update_highest_message.json"

CREDENTIALS_FILENAME = os.path.expanduser("~/.pushover-client-creds.json")

CURRENT_TIME = datetime.strftime("%Y%m%d%X%x%Z")
# device name is up to 25 chars, [A-Za-z0-9_-]
NEW_DEVICE_NAME = "python-{current_time}".format(current_time=CURRENT_TIME)
if not os.path.isfile(CREDENTIALS_FILENAME):
    print('Credentials file not found. Please create.')
    exit(1)

with open(CREDENTIALS_FILENAME, "r") as credentials_file:
    credentials = json.load(credentials_file)

login_payload = {
    "email": credentials['email'],
    "password": credentials['password']
}

login_request = requests.post(ENDPOINT_LOGIN, data=login_payload)

if login_request.status_code == 412:
    twofa = input("Your account is configured for 2FA, "\
                  "please enter the code: ")
    login_form.update({"twofa": twofa})

login_json = json.loads(login_request.text)

if not login_json == 1:
    print("Authentication error; please check your credentials.")
    exit(2)

print(login_request.status_code)
print(login_request.text)

device_registration_payload = {
    "secret": login_json["secret"]
}
device_registration_request = requests.post(ENDPOINT_DEVICES, data=login_form)
