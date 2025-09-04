from abc import ABC, abstractmethod

from tth.api.artifact import ArtifactAPI
from tth.api.execution import ExecutionAPI
from tth.api.report import ReportAPI
from tth.api.trigger import TriggerAPI


class APIClient(ABC):
    """
    API client abstract class that defines abstract methods that each derived class should define.

    Attributes:
        url (str): Typhoon Test Hub url
    """

    def __init__(self, url):
        """
       Constructs API client object.

       Parameters:
           url (str): Typhoon Test Hub url
       """
        self.url = url

    @abstractmethod
    def test_credentials(self):
        """
        Tests if provided credentials are valid
        """
        pass

    @abstractmethod
    def get_request_headers(self):
        """
        Generates dictionary with request header parameters
        """
        pass

    @property
    def trigger(self):
        """
        An object for interacting with Trigger API.
        """
        return TriggerAPI(client=self)

    @property
    def execution(self):
        """
        An object for interacting with Execution API.
        """
        return ExecutionAPI(client=self)

    @property
    def report(self):
        """
        An object for interacting with Report API.
        """
        return ReportAPI(client=self)

    @property
    def artifact(self):
        """
        An object for interacting with Artifact API.
        """
        return ArtifactAPI(client=self)
