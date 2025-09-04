from allure_commons._allure import StepContext
from allure_pytest.utils import get_status

from tth.utils.exception import InvalidDataException


class TestRecord(StepContext):
    _current_test_records = {}

    def __init__(self, record_id, record_message):
        self.record_id = record_id
        self.record_message = record_message
        super().__init__(record_message, {'record_id': record_id})

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        TestRecord._current_test_records[self.record_id] = get_status(exc_val)
        super().__exit__(exc_type, exc_val, exc_tb)

    @classmethod
    def clear_records(cls):
        cls._current_test_records.clear()

    @classmethod
    def get_records(cls):
        return cls._current_test_records


def tth_record(record_id, record_message=None):
    """
    Adds new step in allure report that organizes more functions and report messages in one logical
    group. It can be viewed as tool for better report organization.

    Args:
        record_id (str): identifier of step
        record_message (str, optional): message that is shown in Allure report; default value is record_id value

    Returns:
        step (TestRecord): Allure report step with additional attributes


    Raises:
        InvalidDataException: Invalid arguments provided
    """

    if record_id is None or not isinstance(record_id, str):
        raise InvalidDataException('Record identifier should be a string instance.')

    if record_message is None:
        record_message = record_id

    if not isinstance(record_message, str):
        raise InvalidDataException('Record message should be a string instance.')

    return TestRecord(record_id, record_message)
