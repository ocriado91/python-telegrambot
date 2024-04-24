#!/usr/bin/env python3
"""
Unit Testing for TelegramBot
"""

from datetime import datetime, timezone
import os
from unittest.mock import patch
import requests
import pytest

import telegrambot

# Define an Unix Timestamp into the future (Friday, April 2, 3024 7:00:10 AM)
# to mock the response of getUpdates request
MOCK_FUTURE_DATE_UNIX_TIMESTAMP=33268950010

@pytest.fixture
def mock_now():
    '''
    Mock datetime.now time to improve test reliability
    '''
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 4, 1,
                                                  tzinfo=timezone.utc)
        return mock_datetime.now.return_value

def test_read_valid_config():
    """
    Try to read a valid configuration file
    """

    # Read testing configuration file and check API_KEY value
    data = telegrambot.read_config_file("test/config.toml")
    assert data["API_KEY"] == "TEST_API_KEY"


def test_read_invalid_config():
    """
    Check the raise of exception to try to read
    an invalid configuration file
    """

    # Read non-existent configuration file (returns empty data)
    data = telegrambot.read_config_file("invalid_config.toml")
    assert not data


def test_telegrambot_init():
    """
    Check the default values defined into Telegrambot init method
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Check bot attributes
    assert bot.api_key == "TEST_API_KEY"
    assert bot.url == "https://api.telegram.org/botTEST_API_KEY/"


@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_new_message(requests_mock, mock_now):
    """
    Test check new message functionality
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Mocking /getUpdates post request
    mock_response = {
        "ok": True,
        "result": [
            {"message": {"message_id": 80,
                         "chat": {"id": 12345},
                         "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP}}]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Check successfully reception of incoming message according
    # with the mocking response of /getUpdates post request
    assert bot.check_new_message(mock_now)


@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_new_message_error(mock_now):
    """
    Test check new message functionality when a POST requests
    raises a requests Connection Error
    """

    # With requests-mock plugin, it is required to pass a URL and response
    # to mock object. For check successful requests' ConnectionError handling,
    # its better to define a new mocker object and pass the exception as
    # side_effect
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()

        # Initialize TelegramBot passing the testing configuration file
        data = telegrambot.read_config_file("test/config.toml")
        bot = telegrambot.TelegramBot(data)

        # Return false according with
        assert not bot.check_new_message(mock_now)


@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_old_message(requests_mock, mock_now):
    """
    Test check new message functionality
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Mocking /getUpdates post request
    mock_response = {
        "ok": True,
        "result": [
            {"message":
                {"message_id": 80,
                 "chat": {"id": 12345},
                 "date": 0}}] # Use initial UTC time as message date
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Check False returning due to the message returning
    # by /getUpdates request is in the past

    assert not bot.check_new_message(mock_now)


@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_error_update(requests_mock, mock_now):
    """
    Check no update detection.
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {"ok":False,"result":[]}
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    assert not bot.check_new_message(mock_now)

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_not_update(requests_mock, mock_now):
    """
    Check no update detection.
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {"ok":True,"result":[]}
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    assert not bot.check_new_message(mock_now)

def test_send_message(requests_mock):
    """
    Check successfully send of message to Telegram Bot API.
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define a successfully response into /sendMessage post requests
    mock_response = {
        "ok": True,
    }
    requests_mock.post(f"{bot.url}sendMessage", json=mock_response)

    # Check succcessfully return of send_message method
    assert bot.send_message("Hi")

def test_send_message_error(requests_mock):
    """
    Check a message sending but the Telegram Bot API
    returns an error.
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define the mocking response of error into /sendMessage post
    # requests response
    mock_response = {
        "ok": False,
    }
    requests_mock.post(f"{bot.url}sendMessage", json=mock_response)

    # Check False return of send_message method due to error response into
    # post request
    assert not bot.send_message("Hi")


def test_send_photo(requests_mock):
    """
    Check a photo sending.
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "ok": True,
        "error_code": 200
    }
    requests_mock.post(f"{bot.url}sendPhoto", json=mock_response)

    assert bot.send_photo("mock_photo")

def test_send_audio(requests_mock):
    """
    Check a audio sending.
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "ok": True,
        "error_code": 200
    }
    requests_mock.post(f"{bot.url}sendAudio", json=mock_response)

    assert bot.send_audio("mock_audio")

def test_send_video(requests_mock):
    """
    Check a message sending.
    """

    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {
        "ok": True,
        "error_code": 200
    }
    requests_mock.post(f"{bot.url}sendVideo", json=mock_response)

    assert bot.send_video("mock_video")

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_text_message(requests_mock, mock_now):
    """
    Test to check detection of text incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define the custom mock response of /getUpdates post request
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "text": "Hi",
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.get_message()

    # Check message data values
    assert "text" in  result.keys()
    assert "Hi" in result["text"]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_photo_message(requests_mock, mock_now):
    """
    Test to check detection of photo incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_caption = "test caption"
    expected_file = "hi.png"

    # Mocking response of /getUpdates post request with expected values
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "caption": expected_caption,
                    "photo": [{"file_id":  expected_file}],
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.get_file("photo")

    # Check message data values
    assert "photo" in result.keys()
    assert expected_file == result["photo"][0]
    assert expected_caption == result["photo"][1]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_audio_message(requests_mock, mock_now):
    """
    Test to check detection of audio incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected value of file
    expected_file = "hi.mp4"

    # Mocking response of /getUpdates post request with expected values
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "voice": {"file_id": expected_file},
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract message data
    result = bot.get_file("voice")

    # Check message data values
    assert "voice" in result.keys()
    assert expected_file == result["voice"]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_video_message(requests_mock, mock_now):
    """
    Test to check detection of video incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_file = "hi.mp4"
    expected_caption = "video caption"

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.get_file("video")

    # Check message data values
    assert "video" in result.keys()
    assert expected_file == result["video"][0]
    assert expected_caption == result["video"][1]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_video_message_with_download(requests_mock, mock_now):
    """
    Test to check detection of video incoming message and
    try to download the file
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_file = "hi.mp4"
    expected_caption = "video caption"

    target_folder = "download/"
    # Create download folder in case of it doesn't exist
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)
    # Mock response of /getFile post request
    get_file_mock_response = {
        "ok": 200,
        "result": {
            "file_path": "download/"
        }
    }
    requests_mock.post(f"{bot.url}getFile", json=get_file_mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Patch wget download process
    with patch("wget.download") as mock_download:
        # Extract the message data
        result = bot.get_file(label="video",
                              download_file=True)
        print(result)
        # Check message data values
        assert "video" in result.keys()
        assert expected_file == result["video"][0]
        assert expected_caption == result["video"][1]
        mock_download.assert_called_once()

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_video_message_with_download_error(requests_mock,
                                                             mock_now):
    """
    Test to check detection of video incoming message and
    try to download the file with wrong download folder
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_file = "hi.mp4"
    expected_caption = "video caption"

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)
    # Mock response of /getFile post request
    get_file_mock_response = {
        "ok": 200,
        "result": {
            "file_path": "file"
        }
    }
    requests_mock.post(f"{bot.url}getFile", json=get_file_mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    assert not  bot.get_file(label="video",
                             download_path="wrong_folder",
                             download_file=True)

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_document(requests_mock, mock_now):
    """
    Test to check detection of document incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_file = "document.csv"

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "document": {"file_id": expected_file},
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    result = bot.check_message_type()
    assert "document" in result.keys()
    assert result["document"] == expected_file

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_text(requests_mock, mock_now):
    """
    Test to check detection of text incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define the custom mock response of /getUpdates post request
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "text": "Hi",
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "text" in  result.keys()
    assert "Hi" in result["text"]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_photo(requests_mock, mock_now):
    """
    Test to check detection of photo incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_caption = "test caption"
    expected_file = "hi.png"

    # Mocking response of /getUpdates post request with expected values
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "caption": expected_caption,
                    "photo": [{"file_id":  expected_file}],
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "photo" in result.keys()
    assert expected_file == result["photo"][0]
    assert expected_caption == result["photo"][1]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_audio(requests_mock, mock_now):
    """
    Test to check detection of audio incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected value of file
    expected_file = "hi.mp4"

    # Mocking response of /getUpdates post request with expected values
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "voice": {"file_id": expected_file},
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract message data
    result = bot.check_message_type()

    # Check message data values
    assert "voice" in result.keys()
    assert expected_file == result["voice"]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_video(requests_mock, mock_now):
    """
    Test to check detection of video incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define expected values
    expected_file = "hi.mp4"
    expected_caption = "video caption"

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "video" in result.keys()
    assert expected_file == result["video"][0]
    assert expected_caption == result["video"][1]

@pytest.mark.usefixtures("mock_now")
def test_telegrambot_check_message_type_none(requests_mock, mock_now):
    """
    Test to check detection of invalid format
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "ok": True,
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "other": {"file_id": "other_file"},
                    "date": MOCK_FUTURE_DATE_UNIX_TIMESTAMP
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message(mock_now)

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert not result

def test_telegrambot_get_file(requests_mock):
    """
    Test to check download file method
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # If doesn't exists previously, create the target folder
    target_folder = "download/"
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    # Mock response of /getFile post request
    mock_response = {
        "ok": 200,
        "result": {
            "file_path": target_folder
        }
    }
    requests_mock.post(f"{bot.url}getFile", json=mock_response)

    # Patch wget download process
    with patch("wget.download") as mock_download:
        result = bot.download_file(file_id=1234)

        # Check the properly call to wget download function
        # and the correct result of download_file bot method
        mock_download.assert_called_once()
        assert result

def test_telegrambot_get_file_wrong_folder():
    """
    Test to check get file method in case of wrong folder configured
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # This folder doesn't exist, so the download_file method
    # detects this point and return a False flag
    target_folder = "wrong_download_folder/"

    assert not bot.download_file(file_id=1234,
                                  download_path=target_folder)

def test_telegrambot_get_file_no_ok_response(requests_mock):
    """
    Test to check download file method in case of the
    TelegramBot API response was an error
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # If doesn't exists previously, create the target folder
    target_folder = "download/"
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    # Mock error response of /getFile post request
    mock_response = {
        "ok": False
    }
    requests_mock.post(f"{bot.url}getFile", json=mock_response)

    assert not bot.download_file(file_id=1234,
                                  download_path=target_folder)

