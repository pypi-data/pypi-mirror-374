from tth.uploader.utils import read_or_get

import logging

log = logging.getLogger()

SERVER_IP = read_or_get('', 'TTH_URL', None)
if SERVER_IP is not None:
    log.debug("Typhoon Test Hub URL: " + SERVER_IP)
API_KEY = read_or_get('', 'TTH_API_KEY', None)

UPLOAD_ENDPOINT = SERVER_IP + '/api/reports/upload' if SERVER_IP is not None else None
HISTORY_ENDPOINT = SERVER_IP + '/api/reports/history' if SERVER_IP is not None else None

EXECUTION = read_or_get('', 'TTH_EXECUTION_ID', None)
if EXECUTION is None:
    EXECUTION = read_or_get('', 'EXECUTION_ID', None)


def mandatory_options_provided():
    return not any(variable is None for variable in [SERVER_IP, API_KEY])
