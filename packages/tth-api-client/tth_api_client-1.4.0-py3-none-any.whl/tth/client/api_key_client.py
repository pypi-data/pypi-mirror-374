import requests

from tth.client.client_base import APIClient


class APIKeyClient(APIClient):
    """
    API client class that uses API key for authentication.

    Attributes:
        url (str): Typhoon Test Hub url (e.g. https://foo.bar)
        api_key (str): API key for authentication obtained from the "API Keys" section of Typhoon Test Hub
    """

    def __init__(self, url, api_key):
        self.url = url.rstrip('/')
        self.api_key = api_key
        super().__init__(url)

    def test_credentials(self):
        """
        Tests if provided credentials are valid.

        Returns:
            status (bool): Indicator whether provided credentials are valid
        """
        response = requests.get(f'{self.url}/api/api_keys/test', headers=self.get_request_headers())
        return response.status_code == 200

    def get_request_headers(self):
        """
        Generates dictionary with request header parameters.

        Returns:
            header (dict): Request header parameters
        """
        return {'X-API-Key': str(self.api_key)}
