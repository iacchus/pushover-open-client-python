#!/usr/bin/env python

# Pushover Open Client API
# specification: https://pushover.net/api/client

import datetime
import json
import os
import requests

from pushover_client_python import PushoverOpenClient
from pushover_client_python import PushoverOpenClientRealTime
from pushover_client_python import print_data_errors

now = datetime.datetime.now()
current_time = now.strftime("%Y%m%d_%H%M%S")
dummy_device_name = "python-{current_time}".format(current_time=CURRENT_TIME)

pushover_client = PushoverOpenClient().load_from_credentials_file()

def dummy_login():

    print("Logging in...")
    # Please, improve this :)
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
            print("json:", pushover_client.login_response.json)
            print("text:", pushover_client.login_response.text)
            print("status code:", pushover_client.login_response.status_code)
            errors = pushover_client.login_response_data["errors"]
            print_data_errors(errors=errors)
            exit(1)

    print("Login ok. secret:", secret)

    return secret
secret = dummy_login()

def dummy_register_device():
    print("Registering new device...")

    device_id = pushover_client.register_device()

    if not device_id:
        print("Error registering device.",
              pushover_client.device_registration_response_data)
        print("json:", pushover_client.device_registration_response.json)
        print("text:", pushover_client.device_registration_response.text)
        print("status code:", pushover_client.device_registration_response.status_code)

        errors = pushover_client.device_registration_response_data["errors"]
        print_data_errors(errors=errors)
        exit(2)

    print("Device registered. device_id:", device_id)

    return device_id
device_id = dummy_register_device()

def dummy_message_downloading():
    print("Downloading messages...")

    pushover_client.messages.clear()
    messages = pushover_client.download_messages(device_id="bruh")

    if not messages:
        print("Error downloading messages.",
              pushover_client.message_downloading_response_data)
        print("json:", pushover_client.message_downloading_response.json)
        print("text:", pushover_client.message_downloading_response.text)
        print("status code:", pushover_client.message_downloading_response.status_code)
        errors = pushover_client.message_downloading_response_data["errors"]
        print_data_errors(errors)
        exit(3)

    print("Messages were downloaded. Here they are:", messages)

    return messages
messages = dummy_message_downloading()
number_of_messages_before_deletion = len(messages)
print("MESSAGES:", pushover_client.messages)

def dummy_delete_all_messages():
    print("Let's delete all messages now?")

    messages_before = len(pushover_client.messages)

    is_success = pushover_client.delete_all_messages()
    pushover_client.messages.clear()

    if not is_success:
        print("Error deleting old messages.",
              pushover_client.update_highest_message_response_data)
        print("json:", pushover_client.update_highest_message_response.json)
        print("text:", pushover_client.update_highest_message_response.text)
        print("status code:", pushover_client.update_highest_message_response.status_code)
        errors = pushover_client.update_highest_message_data["errors"]
        print_data_errors(errors=errors)
        exit(4)

    pushover_client.download_messages()
    messages_after = len(pushover_client.messages)

    print("messages_before:", messages_before)
    print("messages_after:", messages_after)
    return messages_after
number_of_messages_after_deletion = dummy_delete_all_messages()

