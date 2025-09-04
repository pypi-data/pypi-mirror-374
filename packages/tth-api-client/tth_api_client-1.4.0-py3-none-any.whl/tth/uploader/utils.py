import json
import math
from configparser import ConfigParser
from datetime import datetime, timezone
from itertools import chain
import logging
import os
import time

import requests

log = logging.getLogger()


def read_variable(file_name, variable_name):
    """
    Reads a variable value from the given config file.
    """
    parser = ConfigParser()
    try:
        with open(file_name) as lines:
            lines = chain(("[top]",), lines)
            parser.read_file(lines)
        var = parser['top'][variable_name]
        if var.upper in ('TRUE', 'FALSE'):
            return bool(var.capitalize())
        return parser['top'][variable_name]
    except IOError as ex:
        # log.fatal(ex)
        return None
    except KeyError as ex:
        log.fatal(ex)
        raise ValueError(f'Variable not found: {variable_name}')


def get_variable(variable_name, default_value=None):
    """
    Reads a variable value from OS environment.
    """
    if variable_name in os.environ:
        value = os.environ[variable_name]
        log.info(f"Reading variable {variable_name} from environment: {value}")
        return value
    else:
        log.info(f"Using default for variable {variable_name}: {default_value}")
        return default_value


def read_or_get(file_name, variable_name, default_value=None):
    """
    Attempts to read a config variable first from the given file, and if not found then from OS environment.
    """
    try:
        value = read_variable(file_name, variable_name)
        if not value:
            value = get_variable(variable_name, default_value)
        return value
    except ValueError as ex:
        raise ex


def local_timestamp_to_utc(local_timestamp):
    epoch_seconds = time.mktime(local_timestamp.timetuple())
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_tags(tags):
    try:
        return [item.strip() for item in tags.split(',')]
    except Exception as e:
        log.fatal(e)
        raise Exception('Tags format is invalid.')


def convert_bytes_to_string(value):
    decimals = 2
    if value == 0:
        return '0 B'

    k = 1024
    dm = 0 if decimals < 0 else decimals
    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    i = math.floor(math.log(value) / math.log(k))

    return f"{round(float(value / math.pow(k, i)), dm)} {sizes[i]}"


def generate_progress_string(bytes_read, bytes_total):
    return f'{str(math.floor(bytes_read / bytes_total * 100)) if bytes_total > 0 else 100}% ' \
           f'({str(convert_bytes_to_string(bytes_read))}/{str(convert_bytes_to_string(bytes_total))})'


def is_artifact_downloadable(artifact_url, headers):
    response = requests.head(artifact_url, allow_redirects=True, headers=headers)
    return response.status_code == 200
