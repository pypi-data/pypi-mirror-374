import logging
import math
import os
import shutil
import tempfile
import threading
import uuid
import zipfile
from datetime import datetime, timezone

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from tth.uploader import utils, report_handler
from tth.utils.exception import APIException, InvalidPathException, InvalidDataException

log = logging.getLogger()


class ArtifactAPI:
    """
    Class that allows for interacting with artifacts via API.

    Attributes:
        client (object): client for sending requests to Typhoon Test Hub API
    """

    def __init__(self, client):
        self.client = client
        self.__locks = {}
        self.__percentages = {}

    def __create_upload_callback(self, execution, name, no_progress_output):
        def callback(monitor):
            if not no_progress_output:
                encoder_len = monitor.encoder.len

                percentage = math.floor(monitor.bytes_read / encoder_len * 100)
                if str(execution) in self.__locks:
                    with self.__locks[str(execution)]:
                        if percentage > self.__percentages[str(execution)]:
                            self.__percentages[str(execution)] = percentage
                            progress_message = utils.generate_progress_string(monitor.bytes_read, encoder_len)
                            log.info(f"Uploading artifact: {name} {progress_message}")

        return callback

    def upload_artifact(self, artifact_path, zip_dir=False, no_progress_output=True, execution_id=None,
                        retention_until=None):
        """
        Upload a new artifact.

        Args:
            artifact_path (str): Path of artifact
            zip_dir (bool, optional): If True, artifact_path should point to a directory which would be zipped and
                uploaded as a single artifact; If False, artifact_path should point to a file which should be uploaded
                as an artifact; default value is False
            no_progress_output (bool, optional): If True, no upload progress logs are shown; default value is True
            execution_id (int, optional): Identifier of the Execution to which the artifact should be assigned
            retention_until (datetime, optional): Timestamp until artifact should be preserved

        Returns:
            identifier (int): Identifier of created artifact

        Raises:
            APIException: Response status code not 201
            InvalidPathException: Invalid artifact path provided
        """
        artifact_absolute_path = os.path.abspath(artifact_path)
        if not os.path.exists(artifact_absolute_path):
            raise InvalidPathException(f"unknown path {artifact_path}")
        if zip_dir:
            if not os.path.isdir(artifact_absolute_path):
                raise InvalidPathException(f"{artifact_path} should be directory")
        else:
            if not os.path.isfile(artifact_absolute_path):
                raise InvalidPathException(f"{artifact_path} should be file because zip_dir is True")

        head, tail = os.path.split(artifact_absolute_path)
        artifact_info = {"name": tail, "path": artifact_absolute_path}
        temp_dir = None
        if zip_dir:
            temp_dir = tempfile.mkdtemp()
            zip_path = report_handler.create_zip_archive_in_directory(tail, artifact_absolute_path, temp_dir)
            head, tail = os.path.split(zip_path)
            artifact_info = {"name": tail, "path": zip_path}
        retention = retention_until
        if retention_until is not None:
            if not isinstance(retention_until, datetime):
                raise InvalidDataException("retention until timestamp should be datetime instance")

            retention = retention_until.astimezone(timezone.utc)
            if retention < datetime.now(timezone.utc):
                raise InvalidDataException("retention until timestamp cannot be in the past")
            retention = retention.isoformat()

        encoder = MultipartEncoder({
            "file": (artifact_info["name"], open(artifact_info["path"], "rb"), "text/plain"),
            "execution_id": str(execution_id),
            "retention_until": retention
        })

        upload_identifier = str(uuid.uuid4())
        callback = self.__create_upload_callback(upload_identifier, artifact_info["name"], no_progress_output)
        monitor = MultipartEncoderMonitor(encoder, callback)

        if not no_progress_output:
            log.info(f"Uploading artifact: {artifact_info['name']} 0%")

        self.__locks[upload_identifier] = threading.Lock()
        self.__percentages[upload_identifier] = 0
        headers = {**{"Content-Type": monitor.content_type}, **self.client.get_request_headers()}
        response = requests.post(f"{self.client.url}/api/artifacts/upload/manual", data=monitor, headers=headers)
        del self.__locks[upload_identifier]
        del self.__percentages[upload_identifier]

        if zip_dir and temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

        if response.status_code == 201:
            artifact_id = response.json()
            return int(artifact_id)
        else:
            raise APIException(response)

    def download_artifact(self, artifact_id, file_name=None, destination='', no_progress_output=True,
                          unzip_archive=False):
        """
        Download an existing artifact from Typhoon Test Hub.

        Args:
            artifact_id (int): Identifier of artifact
            file_name (str, optional): Name of file after download ("save as" under file name);
                default value is the name of the downloaded file under which it was preserved by Typhoon Test Hub
            destination (str, optional): Directory where file is downloaded (and optionally extracted);
                default value is an empty string (file downloaded in working directory)
            no_progress_output (bool, optional): If True, no download progress logs are shown; default value is True
            unzip_archive (bool, optional): If True, downloaded artifact is treated as archive, and extracted via
                unzipping process; default value is True

        Returns:
            path (str): Absolute path of downloaded file

        Raises:
            APIException: Response status code not 200
        """
        artifact_url = f"{self.client.url}/api/downloads/artifacts/{str(artifact_id)}"
        headers = {**{"User-Agent": "Typhoon Officer"}, **self.client.get_request_headers()}
        if not utils.is_artifact_downloadable(artifact_url, headers):
            raise APIException("Artifact is not available")
        download_identifier = str(uuid.uuid4())
        self.__locks[download_identifier] = threading.Lock()
        self.__percentages[download_identifier] = 0

        if not no_progress_output:
            log.info(f"Downloading artifact: {(file_name + ' ') if file_name is not None else ' '} "
                     f"{utils.generate_progress_string(0, 0)}")
        save_as = None
        with requests.post(artifact_url, allow_redirects=True, headers=headers) as response:
            if response.status_code != 200:
                raise APIException(response)
            if file_name is None:
                content = response.headers.get('Content-Disposition', None)
                if content is not None:
                    content_split = content.split('filename=')
                    if len(content_split) > 1:
                        save_as = content_split[1].replace('filename=', '').replace('"', '').strip()
                if save_as is None:
                    save_as = f'downloaded_artifact_{str(artifact_id)}'
            else:
                save_as = file_name
            file_path = os.path.abspath(os.path.join(destination, save_as))
            destination_path = os.path.abspath(os.path.dirname(file_path))
            if not os.path.isdir(destination_path):
                os.makedirs(destination_path, exist_ok=True)

            total_size = int(response.headers.get("Content-Length", 0))
            chunk_size = 10 ** 6
            with open(file_path, mode="wb") as file:
                size = 0
                for data in response.iter_content(chunk_size=chunk_size):
                    size += file.write(data)
                    if not no_progress_output:
                        if total_size > 0:
                            percentage = math.floor(size / total_size * 100)
                            if download_identifier in self.__locks:
                                with self.__locks[download_identifier]:
                                    if percentage > self.__percentages[download_identifier]:
                                        self.__percentages[download_identifier] = percentage
                                        log.info(f"Downloading artifact: {save_as} "
                                                 f"{utils.generate_progress_string(size, total_size)}")
        del self.__locks[download_identifier]
        del self.__percentages[download_identifier]

        if unzip_archive:
            with zipfile.ZipFile(file_path) as zip_ref:
                zip_ref.extractall(destination_path)
        return file_path
