import json
import logging
import subprocess

import os
import uuid
import zipfile
import shutil
from datetime import datetime

import requests

from tth.uploader.constants import *
from tth.uploader.utils import local_timestamp_to_utc
from tth.utils.exception import APIException, InvalidDataException

log = logging.getLogger()


def generate_allure_results(allure_dir):
    out_dir = os.path.join(os.path.dirname(allure_dir), TEMP_ALLURE_RESULTS)
    remove_folder(out_dir)
    shutil.copytree(allure_dir, out_dir)
    return os.path.abspath(out_dir)


def copy_allure_report(allure_dir):
    out_dir = os.path.join(os.path.dirname(allure_dir), TEMP_ALLURE_REPORT)
    remove_folder(out_dir)
    shutil.copytree(allure_dir, out_dir)
    return os.path.abspath(out_dir)


def retrieve_allure_history(allure_temp_results, client=None, execution_id=None):
    log.info("Retrieving report history from Typhoon Test Hub...")
    data = {}
    history_directory = os.path.join(allure_temp_results, "history")
    remove_folder(history_directory)
    os.mkdir(history_directory)
    zip_path = os.path.join(history_directory, "downloaded_history.zip")
    execution_identifier = execution_id
    if client is not None:
        history_endpoint = f"{client.url}/api/reports/history"
        headers = client.get_request_headers()
    else:
        from tth.uploader.settings import HISTORY_ENDPOINT, API_KEY, EXECUTION
        history_endpoint = HISTORY_ENDPOINT
        headers = {'X-API-Key': API_KEY}
        if execution_identifier is None:
            execution_identifier = EXECUTION
        data['execution'] = execution_identifier

    result = requests.post(history_endpoint, data=json.dumps(data), verify=False,
                           headers={**headers, **{'Content-Type': 'application/json'}})
    if result.status_code == 200:
        if result.content != b'None' and result.content is not None:
            try:
                with open(zip_path, 'wb') as zipFile:
                    zipFile.write(result.content)
                with zipfile.ZipFile(zip_path) as zip_ref:
                    zip_ref.extractall(history_directory)
                os.remove(zip_path)
            except Exception as e:
                log.debug(e)
    else:
        raise Exception("Typhoon Test Hub access denied")


def generate_allure_report(allure_results, allure_working_directory):
    log.info("Arranging report for Typhoon Test Hub...")
    out_dir = os.path.abspath(os.path.join(allure_working_directory, TEMP_ALLURE_REPORT))
    if shutil.which('tth-allure') is not None:
        allure_executable = 'tth-allure'
    elif shutil.which('typhoon-allure') is not None:
        allure_executable = 'typhoon-allure'
    elif shutil.which('allure') is not None:
        allure_executable = 'allure'
    else:
        raise ModuleNotFoundError('Allure executable is not found')
    command = f'{allure_executable} generate {allure_results} --clean -o "{out_dir}"'
    subprocess.run(command, shell=True)
    return out_dir


def clean_temp_files(paths):
    for path in paths:
        if path is not None:
            remove_folder(path)


def remove_folder(path):
    try:
        shutil.rmtree(path)
    except Exception as e:
        log.debug(e)


def create_zip_archive(allure_temp_report):
    zip_path = uuid.uuid4().hex.upper() + '.zip'

    zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    __zip_dir(allure_temp_report, zip_file)
    zip_file.close()
    return zip_path


def create_zip_archive_in_directory(name, zipped_directory, destination):
    zip_path = os.path.abspath(os.path.join(destination, name + '.zip'))
    zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    __zip_dir(zipped_directory, zip_file)
    zip_file.close()
    return zip_path


def __zip_dir(path, zip_handler):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            zip_handler.write(file_path, os.path.relpath(file_path, path))


def __is_not_blank(s):
    return bool(s and not s.isspace())


def get_config_option(option, default):
    return option if __is_not_blank(option) else default


def send_report(report_path, tags, started_at, ended_at, execution_id, failed_number=0, broken_number=0,
                passed_number=0, skipped_number=0, unknown_number=0, client=None, report_type='allure',
                test_results=None):
    values = {'started_at': started_at, 'ended_at': ended_at, 'failed': failed_number, 'broken': broken_number,
              'passed': passed_number, 'skipped': skipped_number, 'unknown': unknown_number,
              'report_type': report_type, 'execution': execution_id,
              'tags': json.dumps(tags if tags is not None else []), 'test_results': test_results}
    zip_path = None
    response = None
    if report_type in ['html', 'allure']:
        zip_path = create_zip_archive(report_path)
        file = open(zip_path, 'rb')
    elif report_type == 'pdf':
        file = open(report_path, 'rb')
    else:
        if os.path.isdir(report_path):
            zip_path = create_zip_archive(report_path)
            file = open(zip_path, 'rb')
        else:
            file = open(report_path, 'rb')
    try:
        if client is not None:
            upload_endpoint = f"{client.url}/api/reports/upload"
            headers = client.get_request_headers()
        else:
            from tth.uploader.settings import UPLOAD_ENDPOINT, API_KEY
            upload_endpoint = UPLOAD_ENDPOINT
            headers = {'X-API-Key': API_KEY}

        response = requests.post(upload_endpoint, files={'file': file}, data=values, verify=False,
                                 headers=headers)
        successful_upload = response.status_code == 201
        if not successful_upload:
            log.fatal(f'Data upload is unsuccessful - received response with status code {str(response.status_code)}')
            log.fatal(f'{str(response.reason)}: {str(response.text)}')
    except Exception as e:
        log.debug(e)
        log.fatal("Report could not be uploaded to Typhoon Test Hub")
        successful_upload = False
    file.close()
    if zip_path is not None:
        os.remove(zip_path)

    if response is not None and not successful_upload:
        raise APIException(response)
    try:
        report_id = int(response.json()) if response is not None else None
    except:
        report_id = None

    return successful_upload, report_id


def send_results(results_path, tags, execution_id, multiple_results=False, client=None):
    values = {'execution': execution_id, 'multiple_results': multiple_results,
              'tags': json.dumps(tags if tags is not None else [])}
    response = None
    zip_path = create_zip_archive(results_path)
    file = open(zip_path, 'rb')

    try:
        if client is not None:
            upload_endpoint = f"{client.url}/api/reports/upload"
            headers = client.get_request_headers()
        else:
            from tth.uploader.settings import UPLOAD_ENDPOINT, API_KEY
            upload_endpoint = UPLOAD_ENDPOINT
            headers = {'X-API-Key': API_KEY}

        response = requests.post(upload_endpoint, files={'results': file}, data=values, verify=False,
                                 headers=headers)
        successful_upload = response.status_code == 201
        if not successful_upload:
            log.fatal(f'Data upload is unsuccessful - received response with status code {str(response.status_code)}')
            log.fatal(f'{str(response.reason)}: {str(response.text)}')
    except Exception as e:
        log.debug(e)
        log.fatal("Report could not be uploaded to Typhoon Test Hub")
        successful_upload = False
    file.close()
    if zip_path is not None:
        os.remove(zip_path)

    if response is not None and not successful_upload:
        raise APIException(response)
    try:
        report_id = int(response.json()) if response is not None else None
    except:
        report_id = None

    return successful_upload, report_id


def merge_allure_results(allure_results_directory):
    if allure_results_directory is None:
        raise Exception("Directory containing multiple Allure results is not recognized")
    if os.path.isdir(allure_results_directory):
        allure_results_directories = sorted([f.path for f in os.scandir(allure_results_directory) if f.is_dir()])
        if len(allure_results_directories) == 0:
            raise Exception("Provided directory does not contain Allure results")

        out_dir = os.path.abspath(os.path.join(os.path.dirname(allure_results_directory), ALLURE_MERGED_RESULTS))
        remove_folder(out_dir)

        allure_results_dir = ""
        for allure_dir in allure_results_directories:
            history_path = os.path.join(allure_dir, "history")
            if os.path.isdir(history_path):
                shutil.rmtree(history_path)
            shutil.copytree(allure_dir, os.path.join(out_dir, os.path.basename(allure_dir)))
            single_allure_results_dir = os.path.join(allure_results_dir, out_dir, os.path.basename(allure_dir))
            allure_results_dir += "\"" + os.path.abspath(single_allure_results_dir) + "\" "
        return out_dir, os.path.join(out_dir, os.path.basename(allure_results_directories[0])), allure_results_dir[:-1]

    else:
        raise Exception("Provided path of directory containing multiple Allure results is not valid")


def get_report_summary(allure_temp_report):
    summary_path = os.path.join(allure_temp_report, "widgets", "summary.json")
    summary_path = "{}".format(summary_path)
    if not os.path.isfile(summary_path):
        raise Exception("Allure report structure is invalid")
    with open(summary_path) as summaryFile:
        try:
            summary = json.load(summaryFile)
            summaryFile.close()
            return __extract_timestamp(summary, "start"), __extract_timestamp(summary, "stop"), \
                summary["statistic"]["failed"], summary["statistic"]["broken"], summary["statistic"]["passed"], \
                summary["statistic"]["skipped"], summary["statistic"]["unknown"]
        except Exception as e:
            log.fatal(e)
            raise Exception("Report summary file structure is invalid")


def __extract_timestamp(summary, key):
    if "time" in summary:
        if key in summary["time"]:
            return local_timestamp_to_utc(datetime.fromtimestamp(summary["time"][key] / 1000))
    return local_timestamp_to_utc(datetime.now())


def generate_report_summary(report_path, report_type, summary, summary_json_path):
    if summary is None:
        if report_type == "allure":
            return get_report_summary(report_path)
        else:
            if summary_json_path is not None:
                try:
                    with open(summary_json_path) as json_file:
                        data = json.load(json_file)
                except Exception as e:
                    raise InvalidDataException('summary file content is not in a valid json from')
                return __extract_data_from_summary_json(data)
            else:
                started_at = local_timestamp_to_utc(datetime.now())
                ended_at = local_timestamp_to_utc(datetime.now())
                failed, broken, passed, skipped, unknown = 0, 0, 0, 0, 0
                return started_at, ended_at, failed, broken, passed, skipped, unknown
    else:
        return __extract_data_from_summary_dict(summary)


def __extract_data_from_summary_dict(summary):
    if 'started_at' in summary:
        if not isinstance(summary['started_at'], datetime):
            raise InvalidDataException('started_at parameter of the summary should be a datetime instance')
        started_at = local_timestamp_to_utc(summary['started_at'])
    else:
        started_at = local_timestamp_to_utc(datetime.now())

    if 'ended_at' in summary:
        if not isinstance(summary['ended_at'], datetime):
            raise InvalidDataException('ended_at parameter of the summary should be a datetime instance')
        ended_at = local_timestamp_to_utc(summary['ended_at'])
    else:
        ended_at = local_timestamp_to_utc(datetime.now())

    failed = __extract_numbered_result_from_summary('failed', summary)
    broken = __extract_numbered_result_from_summary('broken', summary)
    passed = __extract_numbered_result_from_summary('passed', summary)
    skipped = __extract_numbered_result_from_summary('skipped', summary)
    unknown = __extract_numbered_result_from_summary('unknown', summary)

    return started_at, ended_at, failed, broken, passed, skipped, unknown


def __extract_data_from_summary_json(summary):
    if 'started_at' in summary:
        try:
            started_at = datetime.fromisoformat(summary['started_at'])
        except Exception as e:
            raise InvalidDataException('started_at parameter of the summary should be in the valid ISO 8601 format')
    else:
        started_at = local_timestamp_to_utc(datetime.now())

    if 'ended_at' in summary:
        try:
            ended_at = datetime.fromisoformat(summary['ended_at'])
        except Exception as e:
            raise InvalidDataException('started_at parameter of the summary should be in the valid ISO 8601 format')
    else:
        ended_at = local_timestamp_to_utc(datetime.now())

    failed = __extract_numbered_result_from_summary('failed', summary)
    broken = __extract_numbered_result_from_summary('broken', summary)
    passed = __extract_numbered_result_from_summary('passed', summary)
    skipped = __extract_numbered_result_from_summary('skipped', summary)
    unknown = __extract_numbered_result_from_summary('unknown', summary)

    return started_at, ended_at, failed, broken, passed, skipped, unknown


def __extract_numbered_result_from_summary(key, summary):
    if key in summary:
        if not isinstance(summary[key], int) or summary[key] < 0:
            raise InvalidDataException(f'{key} parameter of the summary should be a non-negative integer instance')
        value = summary[key]
    else:
        value = 0
    return value


def generate_test_results(test_results, test_results_json_path):
    if test_results is not None:
        __validate_test_results_structure(test_results)
        return json.dumps(test_results)
    else:
        try:
            with open(test_results_json_path) as json_file:
                data = json.load(json_file)
        except Exception as e:
            raise InvalidDataException('results file content is not in a valid json from')
        __validate_test_results_structure(data)
        return json.dumps(data)


def __validate_test_results_structure(data):
    if not isinstance(data, list):
        raise InvalidDataException('results should be a list instance')

    suite_ids = []
    for suite in data:
        __validate_suite_structure(suite, suite_ids)


def __validate_suite_structure(suite, suite_ids):
    test_ids = []
    if not isinstance(suite, dict):
        raise InvalidDataException('suite should be a dictionary instance')

    if 'name' not in suite:
        raise InvalidDataException('name is a mandatory parameter of suite')

    if 'uid' in suite:
        uid = suite['uid'].strip()
        if uid in suite_ids:
            raise InvalidDataException(f'duplicate suite uid {uid}')
        else:
            suite_ids.append(uid)

    if 'tests' not in suite:
        raise InvalidDataException(f'suite {suite["name"]} has no tests')

    if not isinstance(suite['tests'], list):
        raise InvalidDataException('suite tests should be a list instance')

    for test in suite['tests']:
        __validate_test_result_structure(test, test_ids)


def __validate_test_result_structure(test, test_ids):
    if not isinstance(test, dict):
        raise InvalidDataException('test should be a dictionary instance')

    if 'name' not in test:
        raise InvalidDataException('name is a mandatory parameter of test')

    if 'uid' in test:
        uid = test['uid'].strip()
        if uid in test_ids:
            raise InvalidDataException(f'duplicate test uid {uid}')
        else:
            test_ids.append(uid)

    if 'status' not in test:
        raise InvalidDataException(f'test {test["name"]} has no status')

    status = test['status']
    if not isinstance(status, str):
        raise InvalidDataException(f'test {test["name"]} status is not a string instance')

    if status.strip().upper() not in ['PASSED', 'FAILED', 'BROKEN', 'SKIPPED', 'UNKNOWN']:
        raise InvalidDataException(f'test {test["name"]} status has invalid value {status}')
