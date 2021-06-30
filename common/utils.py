import json
import subprocess
import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(".")

import constants


### GENERAL COMMANDS


def get_timestamp():
    now = str(datetime.datetime.now())[:-3]
    now = now.split(".")[0]
    now = now[:-3]
    now = now.replace(" ", "T")
    return now


def load_config(application=None):
    with open(constants.CONFIG_URL, "r") as config_file:
        try:
            config = json.loads(config_file.read())
            if application is not None:
                config = config[application]
        except Exception as e:
            raise Exception("Could not read config.json: " + str(e))

    return config


def pretty_print(json_object):
    print(json.dumps(json_object, indent=4, sort_keys=True))


def execute_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    status = process.wait()

    if status != 0:
        output = error

    return status, output


# print(get_timestamp())