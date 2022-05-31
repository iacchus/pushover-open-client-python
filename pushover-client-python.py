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

now = datetime.datetime.now()
CURRENT_TIME = now.strftime("%Y%m%d_%H%M%S")
# device name is up to 25 chars, [A-Za-z0-9_-]
NEW_DEVICE_NAME = "python-{current_time}".format(current_time=CURRENT_TIME)
print("New device name is:", NEW_DEVICE_NAME, "You can change it's name "\
                                              "via the Pushover website.")

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

if not login_json["status"] == 1:
    print("Authentication error; please check your credentials.")
    exit(2)

print("Login ok.")
#print(login_request.status_code)
#print(login_request.text)
secret = login_json["secret"]
credentials.update({"secret": secret})
with open(CREDENTIALS_FILENAME, "w") as credentials_file:
    credentials = json.dump(credentials_file)

device_registration_payload = {
    "name": NEW_DEVICE_NAME,
    "os": "O",
    "secret": login_json["secret"]
}
device_registration_request = requests.post(ENDPOINT_DEVICES,
                                            data=device_registration_payload)

device_registration_json = json.loads(device_registration_request.text)

if not device_registration_json["status"] == 1:
    print("Error registering device: ", device_registration_json["errors"])
    exit(3)

print("Device registration ok.")

device_id = device_registration_json["id"]

print("Your new device '{new_device_name}' id is {device_id}"\
    .format(new_device_name=NEW_DEVICE_NAME, device_id=device_id))

message_downloading_params = {
    "secret": secret,
    "device_id": device_id
}
message_downloading_request = requests.get(ENDPOINT_MESSAGES, params=message_downloading_params)

message_downloading_json = json.loads(message_downloading_request.text)

if not message_downloading_json["status"] == 1:
    print("Error retrieving messages.")
    exit(4)

for item in message_downloading_json["messages"]:

    print(item)











