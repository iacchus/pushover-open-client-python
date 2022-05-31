#!/usr/bin/env python

import datetime
import json
import os
import requests

import websocket

API_URL = "https://api.pushover.net/1"

ENDPOINT_LOGIN = "{api_url}/users/login.json".format(api_url=API_URL)
ENDPOINT_DEVICES = "{api_url}/devices.json".format(api_url=API_URL)
ENDPOINT_MESSAGES = "{api_url}/messages.json".format(api_url=API_URL)
ENDPOINT_UPDATE_HIGHEST_MESSAGE = \
        "{api_url}/devices/{device_id}/update_highest_message.json"

WEBSOCKETS_SERVER_URL = "wss://client.pushover.net/push"
WEBSOCKETS_LOGIN = "login:{device_id}:{secret}\n"

CREDENTIALS_FILENAME = os.path.expanduser("~/.pushover-client-creds.json")

now = datetime.datetime.now()
CURRENT_TIME = now.strftime("%Y%m%d_%H%M%S")
# device name is up to 25 chars, [A-Za-z0-9_-]
NEW_DEVICE_NAME = "python-{current_time}".format(current_time=CURRENT_TIME)
print("New device name is:", NEW_DEVICE_NAME, "You can change it's name "\
                                              "via the Pushover website.")
class PushoverOpenClient:

    email = str()
    password = str()
    client_id = str()
    secret = str()

    def __init__(self):
        pass

    def load_from_credentials_file(self, file_path=CREDENTIALS_FILENAME):

        if not os.path.isfile(file_path):
            raise Exception("Credentials file '{credentials_file_path}'"
                            " not found. Please create."\
                            .format(credentials_file_path=file_path))

        with open(file_path, "r") as credentials_file:
            credentials = json.load(credentials_file)

        self.email = credentials["email"]
        self.password = credentials["password"]

        if "client_id" in credentials.keys():
            self.client_id = credentials["client_id"]

        if "secret" in credentials.keys():
            self.client_id = credentials["secret"]

    def login(self):
        login_payload = self._get_login_payload()
        login_request = requests.post(ENDPOINT_LOGIN, data=login_payload)

        if login_request.status_code == 412:
            twofa = input("Your account is configured for two-factor"
                          "authentication, please enter the 2FA code"
                          "to proceed: ")
            login_form.update({"twofa": twofa})

        login_json = json.loads(login_request.text)

        if not login_json["status"] == 1:
            print("Authentication error; please check your credentials.")
            exit(2)

        print("Login ok.")

        secret = login_json["secret"]
        credentials.update({"secret": secret})
        with open(CREDENTIALS_FILENAME, "w") as credentials_file:
            json.dump(credentials, credentials_file)
        pass

    # two-factor authentication for the login process
    def set_twofa(self, twofa):
        pass
    def _get_login_payload(self):
        login_payload = {
            "email": self.email,
            "password": self.password
        }

        return login_payload

# if not os.path.isfile(CREDENTIALS_FILENAME):
#     print('Credentials file not found. Please create.')
#     exit(1)
#
# with open(CREDENTIALS_FILENAME, "r") as credentials_file:
#     credentials = json.load(credentials_file)
#
# login_payload = {
#     "email": credentials['email'],
#     "password": credentials['password']
# }

# login_request = requests.post(ENDPOINT_LOGIN, data=login_payload)


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
credentials.update({"device_id": device_id})
with open(CREDENTIALS_FILENAME, "w") as credentials_file:
    credentials = json.dump(credentials, credentials_file)

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

#really_delete = input("Really wanna delete all previous messages? (y/N): ")
#if not really_delete in ('y', 'Y'):
#    print("Ok! old messages are kept.")
#    exit(0)

id_list = list()  # so we can get the highest id using max()

for item in message_downloading_json["messages"]:
    id_list.append(item["id"])

last_message_id = max(id_list)

update_highest_message_endpoint = ENDPOINT_UPDATE_HIGHEST_MESSAGE \
    .format(api_url=API_URL, device_id=device_id)

delete_messages_payload = {
    "message": last_message_id,
    "secret": secret
}
update_highest_message_request = requests.post(update_highest_message_endpoint,
                                               data=delete_messages_payload)
update_highest_message_json = json.loads(update_highest_message_request.text)

if not update_highest_message_json["status"] == 1:
    print("Error deleting previous messages.")
    exit(5)

print("Successfully deleted old messages!")

websockets_login = WEBSOCKETS_LOGIN.format(device_id=device_id, secret=secret)

def on_open(wsapp):
    wsapp.send(websockets_login)

def on_message(wsapp, message):
    print(message)

#websocket.enableTrace(True)
wsapp = websocket.WebSocketApp(WEBSOCKETS_SERVER_URL, on_open=on_open,
                               on_message=on_message)
wsapp.run_forever()
