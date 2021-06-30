import base64
import json

from twilio.rest import Client

import utils
import constants


twilio_config = None
twilio_client = None

# source_phone_number = None


def get_auth_token():
    encoded_token = twilio_config["auth_token"]
    decoded_token = base64.b64decode(encoded_token)
    token_json = json.loads(decoded_token)
    token = token_json["access_token"]
    return token


def initialize_twilio_client():
    global twilio_config
    global twilio_client

    twilio_config = utils.load_config(application = "twilio")

    account_sid = twilio_config["account_sid"]
    auth_token = get_auth_token()

    twilio_client = Client(account_sid, auth_token)



def send_sms(message, target_phone_number = constants.PERSONAL_PHONE_NUMBER):
    global source_phone_number

    source_phone_number = twilio_config["source_phone_number"]

    if target_phone_number != "ALL":
        twilio_client.api.account.messages.create(
            to = target_phone_number,
            from_ = source_phone_number,
            body = message
        )
    else:
        target_phone_numbers = twilio_config["target_phone_numbers"]

        for target_phone_number in target_phone_numbers:
            twilio_client.api.account.messages.create(
                to = target_phone_number,
                from_ = source_phone_number,
                body = message
            )


if __name__ == '__main__':

    initialize_twilio_client()

    send_sms(message1)
    send_sms(message2, target_phone_number = "+18574159383")

