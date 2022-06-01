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

    credentials_filename = CREDENTIALS_FILENAME

    email = str()
    password = str()
    client_id = str()
    secret = str()

    twofa = str()  # two-factor authentication

    needs_twofa = bool()

    messages = dict()  # { message_id: {message_dict...}, }

    login_response = None  # requests.Response
    login_data = dict()

    device_registration_response = None  # requests.Response
    device_registration_data = dict()

    message_downloading_response = None  # requests.Response
    message_downloading_data = dict()

    update_highest_message_response = None  # requests.Response
    update_highest_message_data = dict()

    def __init__(self):
        pass

    def load_from_credentials_file(self, file_path=CREDENTIALS_FILENAME):

        if not os.path.isfile(file_path):
            raise Exception("Credentials file '{credentials_file_path}'"
                            " not found. Please create."\
                            .format(credentials_file_path=file_path))

        with open(file_path, "r") as credentials_file:
            credentials = json.load(credentials_file)

        self.credentials_filename = file_path

        self.email = credentials["email"]
        self.password = credentials["password"]

        if "client_id" in credentials.keys():
            self.client_id = credentials["client_id"]

        if "secret" in credentials.keys():
            self.client_id = credentials["secret"]

    def login(self):
        """
        Logs in with email and password, achieving a `secret` from the API.
        """

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
        else:
            self.needs_twofa = False

        if not login_response_dict["status"] == 1:
            return None

        # else...
        self.secret = login_response_dict["secret"]
        self._write_credentials_file()

        return self.secret

    def set_twofa(self, twofa):
        """
        Sets the code for two-factor authentication,
        if the user has it enabled. After this, `self.login()` should be
        executed again.
        """
        self.twofa = twofa

    def register_device(self, device_name=NEW_DEVICE_NAME):
        """Registers a new client device on the Pushover account."""

        device_registration_payload = \
            self._get_device_registration_payload(device_name=device_name)
        device_registration_response = \
            requests.post(ENDPOINT_DEVICES, data=device_registration_payload)

        device_registration_dict = json.loads(device_registration_response.text)

        self.device_registration_response = device_registration_response
        self.device_registration_data = device_registration_dict

        if not device_registration_dict["status"] == 1:
            return None

        # else...
        self.device_id = device_registration_dict["id"]

        self._write_credentials_file()

        return self.device_id

    def download_messages(self):
        """Downloads all messages currently on this device."""

        message_downloading_params = self._get_message_downloading_params()
        message_downloading_response =\
            requests.get(ENDPOINT_MESSAGES, params=message_downloading_params)

        message_downloading_dict =\
            json.loads(message_downloading_response.text)

        self.message_downloading_response = message_downloading_response
        self.message_downloading_data = message_downloading_dict

        if not message_downloading_dict["status"] == 1:
            return False

        messages = message_downloading_dict["messages"]

        # else...
        for message in messages:
            message_id = message["id"]
            self.messages.update({message_id: message})

        return messages

    #def update_highest_message(self, last_message_id=None):
    def delete_all_messages(self, last_message_id=None):
        """
        Deletes all messages for this device. If not deleted, tey keep
        being downloaded again.
        """

        if not last_message_id:
            last_message_id = self.get_highest_message_id()
        #if not self.messages:
        #    self.download_messages()


        delete_messages_payload =\
            self._get_delete_messages_payload(last_message_id=last_message_id)

        update_highest_message_endpoint =\
            ENDPOINT_UPDATE_HIGHEST_MESSAGE.format(api_url=API_URL,
                                                   device_id=self.device_id)

        update_highest_message_response =\
            requests.post(update_highest_message_endpoint,
                          data=delete_messages_payload)

        update_highest_message_dict =\
            json.loads(update_highest_message_response.text)

        self.update_highest_message_response = update_highest_message_response
        self.update_highest_message_data = update_highest_message_dict

        if not update_highest_message_dict["status"] == 1:
            return False

        # else...
        return True

    def get_highest_message_id(self, redownload=False):

        if redownload:
            self.download_messages()

        if not self.messages:
            self.download_messages()

        id_list = [message["id"] for message in self.messages]
        # id_list = list()
        # for message in self.messages:
        #     id_list.append(message["id"])
        highest_message_id = max([message["id"] for message in self.messages])

        self.highest_message_id = highest_message_id

        return self.highest_message_id

    def write_credentials_file(self, file_path=None):

        if not file_path:
            file_path = self.credentials_filename

        credentials = self._get_credentials_dict()

        with open(file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file)

    def get_websockets_login_string(self):
        websockets_login_string = WEBSOCKETS_LOGIN \
            .format(device_id=self.device_id, secret=self.secret)
        return websockets_login_string


    def _get_delete_messages_payload(self, last_message_id=None):

        if not last_message_id:
            last_message_id = self._get_highest_message_id()

        delete_messages_payload = {
            "message": last_message_id,
            "secret": self.secret
        }

        return delete_messages_payload

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

    def _get_device_registration_payload(self, device_name=NEW_DEVICE_NAME):

        device_registration_payload = {
            "name": device_name,
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


    # def _write_credentials_file(self, file_path=CREDENTIALS_FILENAME):
    #     credentials = self._get_credentials_dict()
    #
    #     with open(file_path, "w") as credentials_file:
    #         json.dump(credentials, credentials_file)

pushover_client = PushoverOpenClient().load_from_credentials_file()

while True:
    secret = pushover_client.login()

    if secret:
        break

    elif not secret and pushover_client.needs_twofa:
        pushover_client.twofa = input("Your account is set up to using "
                                      "two-factor authentication; Please "
                                      "enter your code: ")
        continue

    elif not secret and not pushover_client.needs_twofa:
        print("Error authenticating. Please check your account's credentials",
              pushover_client.login_response_data)
        exit(1)

# "login:{device_id}:{secret}\n"
websockets_login = pushover_client.get_websockets_string()

def on_open(wsapp):
    wsapp.send(websockets_login)

def on_message(wsapp, message):
    print(message)

#websocket.enableTrace(True)
wsapp = websocket.WebSocketApp(WEBSOCKETS_SERVER_URL, on_open=on_open,
                               on_message=on_message)
wsapp.run_forever()
