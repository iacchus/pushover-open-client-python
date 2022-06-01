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

class PushoverOpenClient:

    email = str()
    password = str()
    client_id = str()
    secret = str()

    twofa = str()  # two-factor authentication

    needs_twofa = bool()

    messages = dict()  # { message_id: {message_dict...}, }

    login_response = None  # requests.Response
    login_data = dict()

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

        login_response = requests.post(ENDPOINT_LOGIN, data=login_payload)
        login_response_dict = json.loads(login_response.text)

        self.login_response = login_response
        self.login_data = login_response_dict

        # If this method fails and `self.needs_twofa` is True, the implementor
        # should ask the user for the 2-factor auth code, set it in
        # `self.twofa`, and run this method again.
        if login_response.status_code == 412:
            self.needs_twofa = True
            return None

        if not login_response_dict["status"] == 1:
            return None

        # else...
        self.secret = login_response_dict["secret"]
        self.needs_twofa = False

        self._write_credentials_file()

        return self.secret


    def register_device(self, device_name=NEW_DEVICE_NAME):

        device_registration_payload = self._get_device_registration_payload()
        device_registration_response = \
            requests.post(ENDPOINT_DEVICES, data=device_registration_payload)

        device_registration_dict = json.loads(device_registration_response.text)

        if not device_registration_dict["status"] == 1:
            return False

        # else...
        self.device_id = device_registration_dict["id"]

        self._write_credentials_file()

        return True


    def download_messages(self):

        message_downloading_params = self._get_message_download_params()
        message_downloading_response =\
            requests.get(ENDPOINT_MESSAGES, params=message_downloading_params)

        message_downloading_dict =\
            json.loads(message_downloading_response.text)

        if not message_downloading_dict["status"] == 1:
            return False

        # else...
        for message in message_downloading_dict["messages"]:
            message_id = message["id"]
            self.messages.update({message_id: message})

        return True


    #def update_highest_message(self, last_message_id=None):
    def delete_all_messages(self, last_message_id=None):
        delete_messages_payload =\
            self._get_delete_messages_payload(last_message_id=last_message_id)

        update_highest_message_endpoint = ENDPOINT_UPDATE_HIGHEST_MESSAGE\
                                                .format(api_url=API_URL,
                                                        device_id=self.device_id)

        update_highest_message_response =\
            requests.post(update_highest_message_endpoint,
                          data=delete_messages_payload)

        update_highest_message_dict =\
            json.loads(update_highest_message_response.text)

        if not update_highest_message_dict["status"] == 1:
            return False

        # else...
        return True

    def _get_delete_messages_payload(self, last_message_id=None):

        if not last_message_id:
            last_message_id = self._get_highest_message_id()

        delete_messages_payload = {
            "message": last_message_id,
            "secret": self.secret
        }

        return delete_messages_payload


    # two-factor authentication for the login process
    def set_twofa(self, twofa):
        self.twofa = twofa

    def _write_credentials_file(self, file_path=CREDENTIALS_FILENAME):
        credentials = self._get_credentials_dict()

        with open(file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file)

    def _get_credentials_dict(self):
        credentials_dict = dict()

        if self.email: credentials_dict.update({"email": self.email})
        if self.password: credentials_dict.update({"password": self.email})
        if self.secret: credentials_dict.update({"secret": self.email})
        if self.device_id: credentials_dict.update({"device_id": self.email})

        return credentials_dict

    def _get_login_payload(self):
        login_payload = {
            "email": self.email,
            "password": self.password
        }

        if self.twofa:
            login_payload({"twofa": self.twofa})

        return login_payload

    def _get_device_registration_payload(self):

        device_registration_payload = {
            "name": NEW_DEVICE_NAME,
            "os": "O",
            "secret": self.secret
        }

        return device_registration_payload

    def _get_message_downloading_params(self):

        message_downloading_params = {
            "secret": self.secret,
            "device_id": self.device_id
        }

        return message_downloading_params

    def _get_highest_message_id(self):

        id_list = list()

        for message in self.messages
            id_list.append(message["id"])

        self.highest_message_id = max(id_list)

    def _write_credentials_file(self, file_path=CREDENTIALS_FILENAME):
        credentials = self._get_credentials_dict()

        with open(file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file)

pushover_client = PushoverOpenClient().load_from_credentials_file()

websockets_login = WEBSOCKETS_LOGIN.format(device_id=device_id, secret=secret)

def on_open(wsapp):
    wsapp.send(websockets_login)

def on_message(wsapp, message):
    print(message)

#websocket.enableTrace(True)
wsapp = websocket.WebSocketApp(WEBSOCKETS_SERVER_URL, on_open=on_open,
                               on_message=on_message)
wsapp.run_forever()
