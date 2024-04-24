#!/bin/env/python3
"""
This python module provides a interface between the users and our TelegramBot
"""

from datetime import datetime, timezone
import logging
import os
import tomli
import requests
import wget

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def read_config_file(config_file: str) -> dict:
    """
    Read and incoming configuration file
    (into TOML format) and extract the data
    NOTE: This function is external to TelegramBot
    class to allow pass just a dictionary to the
    class (not entire configuration file).

    Parameters:
        - config_file (str): The path to the
        configuration file.

    Returns:
        - dict: A dictionary containing the extracted
        data from the configuration file.

    Raises:
        - FileNotFoundError: If the configuration file
        is not found.

    """

    try:
        with open(config_file, 'rb') as config_reader:
            return tomli.load(config_reader)
    except FileNotFoundError:
        logger.error('Configuration file %s not found', config_file)
        return {}


class TelegramBot:
    """
    This class provides methods for retrieving updates and messages
    from the Telegram API.
    """

    def __init__(self, config: dict):
        logger.info("Starting TelegramBot")
        self.api_key = config["API_KEY"]
        self.url = f"https://api.telegram.org/bot{self.api_key}/"
        self.message_info = {}
        self.last_message_id = 0
        self.chat_id = None

    def _get_updates(self,
                     reference_time: datetime) -> bool:
        """
        Retrieve TelegramBot updates into JSON format

        Parameters:
            - reference_time (datetime): A reference
            time to compare against the message datetime.

        Returns:
            bool: True if updates are successfully retrieved, False otherwise.
        """

        method_url = self.url + "getUpdates"

        # This function is called in first place to retrieve incoming updates.
        # If there is any error into POST requests, catch the exception and
        # return False to avoid the rest of the app try to launch new requests.
        try:
            response = requests.post(method_url,
                                    timeout=10,
                                    data={"offset": -1}).json()
        except requests.exceptions.ConnectionError:
            logger.error("Reached max. number of attempts!")
            return False

        logger.debug("Incoming data: %s", response)

        # Check "ok" field into response
        if not response["ok"]:
            return False

        # The updates are stored 24 hours into Telegram Bot API server. If there
        # aren't any updates stored into this server, the API returns a
        # {"ok":true,"result":[]} JSON response. To check if result list is
        # to check this point.
        if not response["result"]:
            return False

        self.chat_id = response["result"][-1]["message"]["chat"]["id"]
        self.message_info = response["result"][-1]["message"]

        # Extract message datetime and compare against reference time to
        # detect old messages
        date_info = datetime.fromtimestamp(int(self.message_info["date"]),
                                           timezone.utc)
        if date_info < reference_time:
            return False

        return True

    def check_new_message(self,
                          reference_time: datetime) -> bool:
        """
        Method to check if last message in queue is a new one

        Parameters:
            - reference_time (datetime): A reference time
            to compare against the message datetime.

        Returns:
            bool: True if the last message is new, False otherwise.
        """

        if self._get_updates(reference_time):
            message_id = self.message_info["message_id"]
            if message_id != self.last_message_id:
                # Update message ID attribute
                self.last_message_id = message_id
                return True
        return False

    def check_message_type(self):
        """
        Check the incoming message type and return the result
        of the corresponding method.

        Returns:
            - If the incoming message is a text, returns the incoming text.
            - if the incoming message is a photo, audio,  or video, returns
            the file_id and caption (only for photo and video messages)
        """
        logger.debug("Message info %s", self.message_info)
        keys = self.message_info.keys()
        if "text" in keys:
            return self.get_message()
        if "photo" in keys:
            return self.get_file(label="photo")
        if "voice" in keys:
            return self.get_file(label="voice")
        if "video" in keys:
            return self.get_file(label="video")
        if "document" in keys:
            return self.get_file(label="document")
        logger.error("None accepted type detected")
        return None

    def get_message(self) -> dict:
        """
        Retrieve the latest TelegramBot message.

        Returns:
            - dict: A dictionary with the message text
            as value.

        """
        message_info = self.message_info["text"]
        logger.info("Detected text message: %s", message_info)
        return {"text": message_info}

    def send_message(self, message: str) -> bool:
        """
        Send a message (txt)

        Parameters:
            - message (string): Desired message to be sent.

        Returns:
            - boolean: A boolean if sendAudio request to Telegram Bot API
            has been successfully sent or not.
        """
        url = self.url + "sendMessage"
        logger.info("Sending message %s to %s", message, self.chat_id)

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "text": message}
        ).json()

        return response["ok"]

    def get_file(self,
                 label: str,
                 download_path: str = "download/",
                 download_file: bool = False,) -> dict:
        """
        Retrieve the latest picture sent to the bot.

        Parameters:
            - download_path (str): Path to download file (if download_file
            flag is enabled)
            - download_file (bool, optional): Whether to download the
            file or not. Defaults to False.

        Returns:
            - dictionary: A dictionary {type, (file, [caption])] where:
                * type: Type of incoming file: photo, audio or video
                * file: file_id of TelegramBot according with API
                * caption: Optional field. Caption related with the
                incoming file
        """

        # Check if there are multiple fields into incoming
        # message info previously returned as list, or
        # only have a single field, returned as dictionary.
        if isinstance(self.message_info[label], list):
            file_info = self.message_info[label][-1]
        else:
            file_info = self.message_info[label]
        file_id = file_info["file_id"]
        logger.info("Detected %s file: %s", label, file_id)

        # Whether if selected, try to download file into
        # configured folder
        if download_file:
            download_flag = self.download_file(file_id, download_path)
            if not download_flag:
                return {}

        # Extract optional caption field from incoming
        # message and return the file and caption
        # tuple
        if "caption" in self.message_info.keys():
            caption = self.message_info["caption"]
            return {label: (file_id, caption)}

        return {label: (file_id)}

    def send_photo(self, file_id: str):
        """
        Send a picture previously sent to Telegram Bot and stored into
        Telegram's server

        Parameters:
            - file_id (str): The file ID of the photo to be sent.

        Returns:
            - boolean: A boolean if sendAudio request to Telegram Bot API
            has been successfully sent or not.
        """

        url = self.url + "sendPhoto"
        logger.info(
            "Sending photo %s to %s using %s", file_id, self.chat_id, url
        )

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "photo": file_id}
        ).json()

        return response["ok"]

    def send_audio(self, file_id: str) -> bool:
        """
        Send and audio file to the specified chat ID using the Telegram Bot
        API.

        Parameters:
            -   file_id (str): The file ID of the audio to be sent.

        Returns:
            - boolean: A boolean if sendAudio request to Telegram Bot API
            has been successfully sent or not.
        """

        url = self.url + "sendAudio"
        logger.info(
            "Sending audio %s to %s using %s", file_id, self.chat_id, url
        )

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "audio": file_id}
        ).json()

        return response["ok"]

    def send_video(self, file_id: str):
        """
        Send a picture previously sent to Telegram Bot and stored into
        Telegram's server
        """
        url = self.url + "sendVideo"
        logger.info(
            "Sending video %s to %s using %s", file_id, self.chat_id, url
        )

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "video": file_id}
        ).json()

        return response["ok"]

    def download_file(
        self, file_id: str, download_path: str = "download/"
    ) -> bool:
        """
        Extract desired file
        """

        # Check if download folder exists
        if not os.path.isdir(download_path):
            logger.error("%s folder not found", download_path)
            return False

        # Build URL according with Telegram Bot API
        url = self.url + "getFile"
        logger.info("Trying to download %s (%s)", file_id, url)
        response = requests.post(
            url, timeout=10, data={"file_id": file_id}
        ).json()
        logger.debug("Response %s", response)

        # Check successfully response
        if not response["ok"]:
            logger.error("ERROR download file!")
            return False
        logger.debug("Download file response: %s", response)

        # Extract file path attribute from response and build the download
        # url
        file_path = response["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{self.api_key}/"
        download_url = download_url + file_path
        logger.info("Trying to download %s", download_url)

        # Download file with wget
        wget.download(download_url, download_path)
        return True
