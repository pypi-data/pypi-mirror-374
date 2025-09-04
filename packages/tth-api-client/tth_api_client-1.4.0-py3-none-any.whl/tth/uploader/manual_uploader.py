import getopt
import logging
import os
import sys

from tth.utils.exception import UnsupportedReportTypeException, InvalidDataException, InvalidPathException

from tth.uploader.constants import REPORT_TYPES
from tth.uploader.settings import mandatory_options_provided
from tth.uploader.utils import parse_tags
from tth.uploader.report_handler import (retrieve_allure_history, generate_allure_results, send_results, send_report,
                                         copy_allure_report, generate_report_summary, generate_test_results,
                                         clean_temp_files)

log = logging.getLogger()


def manual_upload():
    if not mandatory_options_provided():
        raise Exception("Typhoon Test Hub mandatory environment variables not defined - "
                        "please define TTH_URL and TTH_API_KEY")

    allure_temp_results, allure_temp_report, allure_results_dir = None, None, ""
    (allure_results_directory, report_path, tags, merge_results, report_type, summary_json_path,
     test_results_json) = __get_config_arguments()
    from tth.uploader.settings import EXECUTION
    if EXECUTION is None:
        raise Exception('Execution of the report is not defined')
    try:
        if report_type == 'allure':
            if allure_results_directory is not None:
                allure_temp_results = generate_allure_results(allure_results_directory)
            elif report_path is not None:
                allure_temp_report = copy_allure_report(report_path)
            else:
                raise Exception("Invalid parameter choice")
            final_report_path = allure_temp_report
        else:
            final_report_path = report_path

        if final_report_path is None:
            logging.info('Sending results to Typhoon Test Hub...')
            successful_upload, report_id = send_results(allure_temp_results, tags, merge_results, EXECUTION)
        else:
            retrieve_allure_history(allure_temp_results, execution_id=EXECUTION)
            started_at, ended_at, failed, broken, passed, skipped, unknown = \
                generate_report_summary(report_path, report_type, None, summary_json_path)

            test_results_data = generate_test_results(None, test_results_json) \
                if test_results_json is not None else None

            logging.info('Sending report to Typhoon Test Hub...')
            successful_upload, report_id = send_report(final_report_path, tags, started_at, ended_at, EXECUTION,
                                                       failed, broken, passed, skipped, unknown,
                                                       report_type=report_type,
                                                       test_results=test_results_data)
        if successful_upload:
            log.info('Report is sent to Typhoon Test Hub')
    except Exception as e:
        log.fatal(e)
        raise Exception("Error encountered when uploading report")
    finally:
        clean_temp_files([allure_temp_results, allure_temp_report])


def __get_config_arguments():
    (allure_results_directory, report_path, tags, report_type, merge_results, summary_json_path,
     test_results_json_path) = (None, None, None, None, False, None, None)
    help_text = 'Uploading report that is already generated: \n' + \
                'python -m tth-upload \n' + \
                '--report-path=<directory_with_report> \n' + \
                '--tags=<tag>. \n\n' + \
                'Uploading Allure results: \n' + \
                'python -m tth-upload \n' + \
                '--allure-results-path=<directory_with_allure_results> \n' + \
                '--tags=<tag>. \n\n' + \
                'Either allure-results-path or report-path parameter should be defined. ' + \
                'Defining both parameters would result in Exception so only one of them should be defined. ' + \
                'Parameter tags, is optional.\n' + \
                'By adding --merge-results parameter, <directory_with_allure_results> parameter should point to ' + \
                'a directory with multiple allure-results directories. This would result in generating merged ' + \
                'Allure report consisting of multiple allure-results.\n' + \
                'In addition, you can specify --report-type parameter to specify type of uploaded report. ' + \
                'Supported values are: allure, pdf, html and custom. Default value is allure. For pdf and custom' + \
                'report, --report-path should be a path to a file. For allure and html report, --report-path ' + \
                'should be a path to a directory. In case of pdf, html and custom report, only --report-path is ' + \
                'required and --allure-results-path and --merge-results options are not available.\n' + \
                'More optional parameters are --summary-path which allows specifying path to json file with ' + \
                'report summary and --test-results-path which allows specifying path to json file with ' + \
                'test results. This option can be used when uploading pdf, html or custom report.'
    available_options = ["allure-results-path=", "report-path=", "tags=", "merge-results",
                         "report-type=", "summary-path=", "test-results-path="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", available_options)
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_text)
            sys.exit()
        if opt == "--merge-results":
            merge_results = True
        elif opt == "--allure-results-path":
            allure_results_directory = arg
        elif opt == "--report-path":
            report_path = arg
        elif opt == "--tags":
            tags = arg
        elif opt == "--report-type":
            report_type = arg
        elif opt == "--summary-path":
            summary_json_path = arg
        elif opt == "--test-results-path":
            test_results_json_path = arg

    if report_type is None:
        report_type = "allure"
    else:
        if report_type not in REPORT_TYPES:
            raise UnsupportedReportTypeException(report_type)

    if allure_results_directory is None and report_path is None:
        raise InvalidDataException("either results-path or report-path should be defined - neither is defined")

    if allure_results_directory is not None and report_path is not None:
        raise InvalidDataException("either results-path or report-path should be defined - both are defined")

    if allure_results_directory is not None and not os.path.isdir(allure_results_directory):
        raise InvalidDataException("provided directory path with allure results is invalid")

    if report_type != "allure" and report_path is None:
        raise InvalidDataException("report directory path is not provided")

    if report_type == "allure" and allure_results_directory is None:
        if report_path is None or not os.path.isdir(report_path):
            raise InvalidDataException("provided directory path with report is invalid")

    if report_type == "html" and not os.path.isdir(report_path):
        raise InvalidDataException("provided directory path with html report is not valid directory path")

    if report_type in ["pdf", "custom"] and not os.path.isfile(report_path):
        raise InvalidDataException(f"provided directory path with {report_type} report is not valid file path")

    if summary_json_path is not None and (not os.path.exists(summary_json_path) or
                                          not os.path.isfile(summary_json_path)):
        raise InvalidPathException(f"unknown path of summary json file")

    if test_results_json_path is not None and (not os.path.exists(test_results_json_path) or
                                               not os.path.isfile(test_results_json_path)):
        raise InvalidPathException(f"unknown path of test results json file")

    tth_tags = parse_tags(tags) if tags is not None else None

    return (allure_results_directory, report_path, tth_tags, merge_results, report_type, summary_json_path,
            test_results_json_path)
