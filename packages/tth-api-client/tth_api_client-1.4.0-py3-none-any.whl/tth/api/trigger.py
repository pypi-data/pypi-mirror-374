import requests

from tth.utils.exception import APIException


class TriggerAPI:
    """
   Class that allows for interacting with triggers via API.

   Attributes:
       client (object): client for sending requests to Typhoon Test Hub API
   """

    def __init__(self, client):
        self.client = client

    def start(self, trigger_id, parameters=None):
        """
        Start an event trigger with the provided trigger identifier.

        Args:
            trigger_id (int): Identifier of event trigger
            parameters (dict, optional): Dictionary with trigger parameters; should be left undefined if trigger has no
                parameters; if the trigger has parameters, it should contain pairs parameter_name: parameter_value

        Returns:
            identifier (int): Identifier of the started Execution

        Raises:
            APIException: Response status code not 200
        """
        if parameters is None:
            parameters = []
        else:
            parameters = [{'name': key, 'value': value} for key, value in parameters.items()]

        parameters = {'parameters': parameters}
        response = requests.post(f"{self.client.url}/api/triggers/start/{str(trigger_id)}",
                                 headers=self.client.get_request_headers(), json=parameters)
        if response.status_code == 201:
            execution_id = response.json()
            return int(execution_id)
        else:
            raise APIException(response)
