#!/bin/env/python3
"""
This python module provides a interface between the users and our TelegramBot
"""

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

    def _get_updates(self) -> bool:
        """
        Retrieve TelegramBot updates into JSON format

        Returns:
            bool: True if updates are successfully retrieved, False otherwise.
        """

        method_url = self.url + "getUpdates"
        data = requests.post(method_url, timeout=10, data={"offset": -1}).json()
        if "result" not in data.keys():
            logger.error("None incoming update")
            return False
        self.chat_id = data["result"][-1]["message"]["chat"]["id"]
        self.message_info = data["result"][-1]["message"]
        return True

    def check_new_message(self) -> bool:
        """
        Method to check if last message in queue is a new one

        Returns:
            bool: True if the last message is new, False otherwise.
        """

        if self._get_updates():
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
        logger.info("Processing message type: %s", keys)
        if "text" in keys:
            return self.get_message()
        if "photo" in keys:
            return self.get_photo()
        if "voice" in keys:
            return self.get_audio()
        if "video" in keys:
            return self.get_video()
        logger.error("None accepted type detected")
        return None

    def get_message(self) -> str:
        """
        Retrieve the latest TelegramBot message.

        Returns:
            str: The text of the latest message.

        """
        message = self.message_info["text"]
        logger.info("Detected text message: %s", message)
        return message

    def send_message(self, message: str):
        """
        Send a message (txt)
        """
        url = self.url + "sendMessage"
        logger.info("Sending message %s to %s", message, self.chat_id)

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "text": message}
        ).json()

        return response["error_code"]

    def get_photo(self, download_file: bool = True) -> tuple:
        """
        Retrieve the latest picture sent to the bot.

        Parameters:
            - download_file (bool, optional): Wheter to download the photo
            file or not. Defaults to True.

        Returns:
            - tuple: A tuple containing the file ID of the photo and its
            caption
        """

        caption = self.message_info["caption"]
        photo_info = self.message_info["photo"][-1]
        file_id = photo_info["file_id"]
        logger.info("Detected picture: %s with caption %s", file_id, caption)
        if download_file:
            self._download_file(file_id)
        return file_id, caption

    def send_photo(self, file_id: str):
        """
        Send a picture previously sent to Telegram Bot and stored into
        Telegram's server

        Parameters:
            - file_id (str): The file ID of the photo to be sent.
        """

        url = self.url + "sendPhoto"
        logger.info(
            "Sending photo %s to %s using %s", file_id, self.chat_id, url
        )

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "photo": file_id}
        ).json()

        return response["error_code"]

    def get_audio(self, download_file: bool = True):
        """
        Retrieve the latest audio file sent to the bot.

        Parameters:
            - download_file (bool, optional): Whether to download the audio file
            or not. Defaults to True.

        Returns:
            str: The file ID of the audio file
        """

        audio_info = self.message_info["voice"]
        file_id = audio_info["file_id"]
        logger.info("Detected audio file: %s", file_id)

        if download_file:
            self._download_file(file_id)
        return file_id

    def send_audio(self, file_id: str):
        """
        Send and audio file to the specified chat ID using the Telegram Bot
        API.

        Parameters:
            -   file_id (str): The file ID of the audio to be sent.
        """

        url = self.url + "sendAudio"
        logger.info(
            "Sending audio %s to %s using %s", file_id, self.chat_id, url
        )

        response = requests.post(
            url, timeout=10, data={"chat_id": self.chat_id, "audio": file_id}
        ).json()

        return response["error_code"]

    def get_video(self, download_file: bool = True):
        """
        Retrieve the latest video file sent to the bot
        """
        caption = self.message_info["caption"]
        video_info = self.message_info["video"]
        file_id = video_info["file_id"]
        logger.info("Detected video file: %s", file_id)

        if download_file:
            self._download_file(file_id)
        return file_id, caption

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

        return response["error_code"]

    def _download_file(
        self, file_id: str, download_path: str = "download/"
    ) -> bool:
        """
        Extract desired file
        """

        # Check if download folder exists
        if not os.path.isdir(download_path):
            logger.error("%s folder not found", download_path)
            return True

        # Build URL according with Telegram Bot API
        url = self.url + "getFile"
        logger.info("Trying to download %s (%s)", file_id, url)
        response = requests.post(
            url, timeout=10, data={"file_id": file_id}
        ).json()
        logger.debug("Response %s", response)

        # Check successfully response
        if "ok" not in response.keys():
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
