import time
import requests

from tth.utils.exception import APIException


class ExecutionAPI:
    """
    Class that allows for interacting with executions via API.

    Attributes:
        client (object): client for sending requests to Typhoon Test Hub API
    """

    def __init__(self, client):
        self.client = client

    def get_info(self, execution_id):
        """
        Obtain details of the Execution with the provided execution identifier.

        Args:
            execution_id (int): Identifier of execution

        Returns:
            data (dict): Execution information

        Raises:
            APIException: Response status code not 200
        """
        response = requests.get(f"{self.client.url}/api/executions/status/{str(execution_id)}",
                                headers=self.client.get_request_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise APIException(response)

    def get_status(self, execution_id):
        """
        Obtain status of the Execution with the provided execution identifier.

        Args:
            execution_id (int): Identifier of execution

        Returns:
            status (str): Execution status

        Raises:
            APIException: Response status code not 200
        """
        response = requests.get(f"{self.client.url}/api/executions/status/{str(execution_id)}",
                                headers=self.client.get_request_headers())
        if response.status_code == 200:
            return response.json()['status']
        else:
            raise APIException(response)

    def wait_until_finished(self, execution_id, interval=10, timeout=None, ignore_errors=False):
        """
        Periodically check the selected Execution's status and waits for the Execution to finish.

        Args:
            execution_id (int): Identifier of execution
            interval (int): Short polling interval for checking execution status
            timeout (int): Timeout (in seconds) of waiting for execution to finish
            ignore_errors (bool): Ignore APIException instances if happen (useful when internet connection is unstable)

        Returns:
            status(str): Execution status

        Raises:
            APIException: Response status code not 200 if ignore_error is False
        """
        start_epoch = int(time.time())
        while True:
            try:
                status = self.get_status(execution_id)
                if status not in ['QUEUED', 'RUNNING']:
                    break

                if timeout is not None:
                    current_epoch = int(time.time())
                    if (current_epoch - start_epoch) > timeout:
                        raise TimeoutError(f'Timeout of {str(timeout)} seconds reached.')
            except APIException as e:
                if not ignore_errors:
                    raise e

            time.sleep(int(interval))
        return status

    def download_artifacts(self, execution_id, expression, destination='', no_progress_output=True):
        """
        Download artifacts belonging to the Execution matching provided expression.

        Args:
            execution_id (int): Identifier of execution
            expression (str): Artifacts selection expression
            destination (str): Directory where file is downloaded; default value is an empty string (file downloaded in
                working directory)
            no_progress_output (bool, optional): If True, no download progress logs are shown; default value is True

        Raises:
            APIException: Response status code not 200
        """
        request_data = {'option': 'SPECIFIC', 'execution': str(execution_id),
                        'executions': [str(execution_id)], 'collect': expression}
        response = requests.post(f"{self.client.url}/api/downloads/available/artifacts",
                                 headers=self.client.get_request_headers(), json=request_data)
        if response.status_code == 200:
            artifacts = response.json()
            if artifacts is None or len(artifacts) == 0:
                raise APIException("No artifacts matching expression were found.")

            for artifact in artifacts:
                self.client.artifact.download_artifact(artifact["id"], artifact["name"],
                                                       destination, no_progress_output)
        else:
            raise APIException(response)
