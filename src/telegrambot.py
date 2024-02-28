#!/bin/env/python3
"""
This python module provides a interface between the users and our TelegramBot
through REST API.
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
    """

    try:
        with open(config_file, 'rb') as config_reader:
            return tomli.load(config_reader)
    except FileNotFoundError:
        logger.error('Configuration file %s not found', config_file)
        return {}


class TelegramBot:
    """
    This class represents a Telegram Bot. It provides methods for retrieving
    updates and messages from the Telegram API.
    """

    def __init__(self, config: dict):
        logger.info("Starting TelegramBot")
        self.api_key = config["API_TELEGRAMBOT_KEY"]
        self.url = f"https://api.telegram.org/bot{self.api_key}/"
        self.message_info = {}
        self.last_message_id = 0
        self.chat_id = None

    def _get_updates(self) -> bool:
        """
        Retrieve TelegramBot updates into JSON format
        """
        method_url = self.url + "getUpdates"
        data = requests.get(method_url, timeout=10, data={"offset": -1}).json()
        if "result" not in data.keys():
            logger.error("None incoming update")
            return False
        self.chat_id = data["result"][-1]["message"]["chat"]["id"]
        self.message_info = data["result"][-1]["message"]
        return True

    def check_new_message(self) -> bool:
        """
        Method to check if last message in queue is a new one
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
        Check the incoming message type:
            - text
            - photo
        """
        logger.debug("Message info %s", self.message_info)
        keys = self.message_info.keys()
        logger.info("Processing message type: %s", keys)
        if "text" in keys:
            message = self.get_message()
            self.send_message(message)
        elif "photo" in keys:
            photo_id = self.get_photo()
            self.send_photo(photo_id)
        elif "voice" in keys:
            audio_id = self.get_audio()
            self.send_audio(audio_id)
        elif "video" in keys:
            video_id = self.get_video()
            self.send_video(video_id)
        else:
            logger.error("None accepted type detected")
            return False
        return True

    def get_message(self):
        """
        Retrieve the latest TelegramBot message
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

        requests.get(
            url, timeout=10, data={"chat_id": self.chat_id, "text": message}
        ).json()

    def get_photo(self, download_file: bool = True):
        """
        Retrieve the latest picture sent to the bot
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
        """
        url = self.url + "sendPhoto"
        logger.info(
            "Sending photo %s to %s using %s", file_id, self.chat_id, url
        )

        requests.get(
            url, timeout=10, data={"chat_id": self.chat_id, "photo": file_id}
        ).json()

    def get_audio(self, download_file: bool = True):
        """
        Retrieve the latest audio file sent to the bot
        """
        audio_info = self.message_info["voice"]
        file_id = audio_info["file_id"]
        logger.info("Detected audio file: %s", file_id)
        if download_file:
            self._download_file(file_id)
        return file_id

    def send_audio(self, file_id: str):
        """
        Send and audio file according with its file ID value
        """
        url = self.url + "sendAudio"
        logger.info(
            "Sending audio %s to %s using %s", file_id, self.chat_id, url
        )

        requests.get(
            url, timeout=10, data={"chat_id": self.chat_id, "audio": file_id}
        ).json()

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

        requests.get(
            url, timeout=10, data={"chat_id": self.chat_id, "video": file_id}
        ).json()

    def _download_file(
        self, file_id: str, download_path: str = "download/"
    ) -> bool:
        """
        Extract desired file
        """

        if not os.path.isdir(download_path):
            logger.error("%s folder not found", download_path)
            return True

        url = self.url + "getFile"
        logger.info("Trying to download %s (%s)", file_id, url)

        response = requests.get(
            url, timeout=10, data={"file_id": file_id}
        ).json()
        logger.debug("Response %s", response)
        if "ok" not in response.keys():
            return False
        logger.debug("Download file response: %s", response)
        file_path = response["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{self.api_key}/"
        download_url = download_url + file_path
        logger.info("Trying to download %s", download_url)
        wget.download(download_url, download_path)
