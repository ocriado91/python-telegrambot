#!/usr/bin/env python3
"""
Unit Testing for TelegramBot
"""

import os
import pytest
import urllib

import telegrambot



def test_read_valid_config():
    """
    This test try to read a valid configuration file
    """

    data = telegrambot.read_config_file("test/config.toml")
    assert data["API_KEY"] == "TEST_API_KEY"


def test_read_invalid_config():
    """
    This test check the raise of exception to try to read
    an invalid configuration file
    """

    data = telegrambot.read_config_file("invalid_config.toml")
    assert not data


def test_telegrambot_init():
    """
    Check the default values defined into Telegrambot init method
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    assert bot.api_key == "TEST_API_KEY"
    assert bot.url == "https://api.telegram.org/botTEST_API_KEY/"


def test_telegrambot_check_new_message(requests_mock):
    """
    Test check new message functionality
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [{"message": {"message_id": 80, "chat": {"id": 12345}}}]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    assert bot.check_new_message()


def test_telegrambot_check_not_update(requests_mock):
    """
    Check no update detection.
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {}
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    assert not bot.check_new_message()


def test_telegrambot_check_text_message(requests_mock):
    """
    Test to check detection of text incoming message
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "text": "Hi",
                }
            }
        ]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    requests_mock.get(f"{bot.url}sendMessage", json={"text": "Hi"})
    bot.check_new_message()
    assert bot.check_message_type()


def test_telegrambot_check_photo_message(requests_mock):
    """
    Test to check detection of photo incoming message
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "caption": "test caption",
                    "photo": [{"file_id": "hi.png"}],
                }
            }
        ]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    requests_mock.get(f"{bot.url}getFile", json={"text": "Hi"})
    requests_mock.get(f"{bot.url}sendPhoto", json={"text": "Hi"})
    bot.check_new_message()
    assert bot.check_message_type()


def test_telegrambot_check_audio_message(requests_mock):
    """
    Test to check detection of audio incoming message
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "voice": {"file_id": "hi.mp4"},
                }
            }
        ]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    requests_mock.get(f"{bot.url}getFile", json={"text": "Hi"})
    requests_mock.get(f"{bot.url}sendAudio", json={"text": "Hi"})
    bot.check_new_message()
    assert bot.check_message_type()


def test_telegrambot_check_video_message(requests_mock):
    """
    Test to check detection of video incoming message
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": "hi.mp4"},
                    "caption": "video caption",
                }
            }
        ]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    requests_mock.get(f"{bot.url}getFile", json={"text": "Hi"})
    requests_mock.get(f"{bot.url}sendVideo", json={"text": "Hi"})

    # Create download folder if doesn't exist
    if not os.path.isdir('download/'):
        os.mkdir('download/')
    bot.check_new_message()
    assert bot.check_message_type()


def test_telegrambot_get_file(requests_mock):
    """
    Test to check getFile method behaviour
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "ok": 200,
        "result": {
            "file_path": "download/"
        }
    }
    requests_mock.get(f"{bot.url}getFile", json=mock_response)

    with pytest.raises(urllib.error.HTTPError):
        bot._download_file(file_id=1234)


def test_telegrambot_get_file_wrong_folder(requests_mock):
    """
    Test to check getFile method behaviour with a wrong folder path
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "ok": 200,
        "result": {
            "file_path": "download/"
        }
    }
    requests_mock.get(f"{bot.url}getFile", json=mock_response)

    bot._download_file(file_id=1234, download_path="wrong_download/")


def test_telegrambot_check_invalid_message(requests_mock):
    """
    Test to check detection of text incoming message
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "result": [{"message": {"message_id": 80, "chat": {"id": 12345}}}]
    }
    requests_mock.get(f"{bot.url}getUpdates", json=mock_response)
    bot.check_new_message()
    assert not bot.check_message_type()
