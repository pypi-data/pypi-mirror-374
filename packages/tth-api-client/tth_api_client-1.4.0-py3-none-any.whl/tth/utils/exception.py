import json


class APIException(Exception):
    """Raise when API call returns error status code"""

    def __init__(self, response):
        text = ''
        if hasattr(response, 'text'):
            if len(response.text) > 0:
                try:
                    text_data = json.loads(response.text)
                    if 'detail' in text_data:
                        text = str(text_data['detail'])
                    elif 'text' in text_data:
                        text = str(text_data['text'])
                    elif 'reason' in text_data:
                        text = str(text_data['reason'])
                    elif 'error' in text_data:
                        text = str(text_data['error'])
                    elif isinstance(text_data, list):
                        text = ','.join(text_data)
                    else:
                        text = response.text
                except:
                    text = response.text
        error_text = '' if len(text) == 0 else f' - {text}'
        if hasattr(response, 'status_code'):
            message = f'Server responded with status: {str(response.status_code)}: {str(response.reason)}{error_text}'
        else:
            message = str(response)
        super().__init__(message)


class UnsupportedReportTypeException(Exception):
    """Raise when invalid report type chosen"""

    def __init__(self, value):
        message = f'Unsupported report type {value}'
        super().__init__(message)


class InvalidPathException(Exception):
    """Raise when invalid directory or file path"""

    def __init__(self, value):
        message = f'Invalid path: {value}'
        super().__init__(message)


class InvalidDataException(Exception):
    """Raise when invalid data"""

    def __init__(self, value):
        message = f'Invalid data provided: {value}'
        super().__init__(message)
