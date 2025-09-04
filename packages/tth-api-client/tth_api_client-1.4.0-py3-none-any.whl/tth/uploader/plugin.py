import json
import logging
import os

import allure
import pytest
import doctest

from tth.data.record import TestRecord
from tth.uploader.report_handler import get_config_option, retrieve_allure_history, generate_allure_results, \
    generate_allure_report, clean_temp_files, send_report, get_report_summary, send_results
from tth.uploader.utils import parse_tags
from tth.uploader.settings import mandatory_options_provided
from tth.utils.exception import APIException

log = logging.getLogger()
test_results = {}


def pytest_addoption(parser):
    parser.addoption("--tth-upload", action="store_true",
                     help="If defined, uploads Allure report to Typhoon Test Hub")
    parser.addoption("--typhoon-upload", action="store_true",
                     help="If defined, uploads Allure report to Typhoon Test Hub")
    parser.addoption("--report-tags", action="store", default=None,
                     help="Presents tags of report, e.g. --report-tags=TAG_NAMES; Deprecated in favour of --tth-tags")
    parser.addoption("--tth-tags", action="store", default=None,
                     help="Presents tags of execution, e.g. --tth-tags=TAG_NAMES")
    parser.addoption("--tth-live", action="store_true",
                     help="Log start and finish of each test")


def __log_tth_live_pytest_log(log_type, name, result, current_test, total_tests):
    print(f"###AGENT_LOG: Pytest session - {log_type} - {name} - {result} - {str(current_test)} - {str(total_tests)}")


@pytest.hookimpl(trylast=True)
def pytest_collection_finish(session):
    if session.config.getoption("--tth-live"):
        __log_tth_live_pytest_log("START SESSION", "", "", 0, len(session.items))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    if item.session.config.getoption("--tth-live"):
        test_results[item.nodeid] = "passed"
        index = 0
        try:
            index = item.session.items.index(item)
            index += 1
        except Exception as e:
            pass

        __log_tth_live_pytest_log("START TEST", item.nodeid, "", index, item.session.testscollected)


# noinspection PyTypeHints
def _exception_breaking_test(exception):
    return not isinstance(exception, (
        AssertionError,
        pytest.fail.Exception,
        doctest.DocTestFailure
    ))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    TestRecord.clear_records()


def attach_test_records(call):
    if call.when == "call":
        records = TestRecord.get_records()
        if records:

            allure.attach(
                body=json.dumps(records, indent=4),
                name=f"TTH Records",
                attachment_type=allure.attachment_type.JSON
            )


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_makereport(item, call):
    attach_test_records(call)

    if item.session.config.getoption("--tth-live"):
        try:
            result = (yield).get_result()
            status = result.outcome

            if call.excinfo:
                exception = call.excinfo.value
                if status != "skipped" and _exception_breaking_test(exception):
                    status = "broken"
            if status != "passed":
                test_results[item.nodeid] = status
            if result.when == "teardown":
                __log_tth_live_pytest_log("STOP TEST", item.name, test_results[item.nodeid], 0,
                                          item.session.testscollected)
        except:
            yield
    else:
        yield


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_sessionfinish(session):
    if session.config.getoption("--tth-live"):
        __log_tth_live_pytest_log("STOP SESSION", "", "", session.testscollected, session.testscollected)
        test_results.clear()

    if session.config.getoption("--tth-upload") or session.config.getoption("--typhoon-upload"):
        if not mandatory_options_provided():
            raise Exception("Typhoon Test Hub mandatory environment variables not defined - "
                            "please define TTH_URL and TTH_API_KEY")

        tags = get_config_option(session.config.getoption("--tth-tags"), None)
        if tags is None:
            if session.config.getoption("--report-tags"):
                log.warning('Option --report-tags is deprecated and will be removed in a future release. '
                            'Please use option --tth-tags.')
            tags = get_config_option(session.config.getoption("--report-tags"), None)
        tags = parse_tags(tags) if tags is not None else None

        from tth.uploader.settings import EXECUTION
        if EXECUTION is None:
            raise Exception('Execution of the report is not defined')

        allure_dir = session.config.getoption('--alluredir')
        if not allure_dir:
            allure_dir = 'allure-results'

        allure_temp_results, allure_temp_report = None, None
        try:
            if not os.path.exists(allure_dir):
                return
            allure_temp_results = generate_allure_results(allure_dir)
            retrieve_allure_history(allure_temp_results)

            log.info('Sending report to Typhoon Test Hub...')
            try:
                successful_upload, report_id = send_results(allure_temp_results, tags, EXECUTION)
            except APIException as e:
                successful_upload = False

            if successful_upload:
                log.info('Report is sent to Typhoon Test Hub')
            else:
                allure_temp_report = \
                    generate_allure_report('"' + allure_temp_results + '"',
                                           os.path.abspath(os.path.dirname(allure_dir)))

                started_at, ended_at, failed, broken, passed, skipped, unknown = \
                    get_report_summary(allure_temp_report)
                log.warning('Uploading Allure results was not successful. Trying to upload Allure report.')
                log.warning('Automatic upload of Allure report is deprecated and will be removed in a future release '
                            'in favour of uploading Allure results.')
                successful_upload, report_id = send_report(allure_temp_report, tags, started_at, ended_at,
                                                           EXECUTION, failed, broken, passed, skipped, unknown)
                if successful_upload:
                    log.info('Report is sent to Typhoon Test Hub')
        except Exception as e:
            log.fatal(e)
        finally:
            clean_temp_files([allure_temp_results, allure_temp_report])
    yield
