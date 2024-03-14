#!/usr/bin/env python3
"""
Unit Testing for TelegramBot
"""

import os
from unittest.mock import patch

import telegrambot


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


def test_telegrambot_check_new_message(requests_mock):
    """
    Test check new message functionality
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Mocking /getUpdates post request
    mock_response = {
        "result": [{"message": {"message_id": 80, "chat": {"id": 12345}}}]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Check successfully reception of incoming message according
    # with the mocking response of /getUpdates post request
    assert bot.check_new_message()


def test_telegrambot_check_not_update(requests_mock):
    """
    Check no update detection.
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    mock_response = {}
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)
    assert not bot.check_new_message()

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

def test_telegrambot_check_text_message(requests_mock):
    """
    Test to check detection of text incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define the custom mock response of /getUpdates post request
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
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.get_message()

    # Check message data values
    assert "text" in  result.keys()
    assert "Hi" in result["text"]

def test_telegrambot_check_photo_message(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "caption": expected_caption,
                    "photo": [{"file_id":  expected_file}],
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.get_file("photo")

    # Check message data values
    assert "photo" in result.keys()
    assert expected_file == result["photo"][0]
    assert expected_caption == result["photo"][1]

def test_telegrambot_check_audio_message(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "voice": {"file_id": expected_file},
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract message data
    result = bot.get_file("voice")

    # Check message data values
    assert "voice" in result.keys()
    assert expected_file == result["voice"]

def test_telegrambot_check_video_message(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.get_file("video")

    # Check message data values
    assert "video" in result.keys()
    assert expected_file == result["video"][0]
    assert expected_caption == result["video"][1]

def test_telegrambot_check_video_message_with_download(requests_mock):
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

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
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
    bot.check_new_message()

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
        assert mock_download.assert_awaited_once()

def test_telegrambot_check_video_message_with_download_error(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
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
    bot.check_new_message()

    assert not  bot.get_file(label="video",
                             download_path="wrong_folder",
                             download_file=True)

def test_telegrambot_check_message_type_text(requests_mock):
    """
    Test to check detection of text incoming message
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Define the custom mock response of /getUpdates post request
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
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "text" in  result.keys()
    assert "Hi" in result["text"]

def test_telegrambot_check_message_type_photo(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "caption": expected_caption,
                    "photo": [{"file_id":  expected_file}],
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "photo" in result.keys()
    assert expected_file == result["photo"][0]
    assert expected_caption == result["photo"][1]

def test_telegrambot_check_message_type_audio(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "voice": {"file_id": expected_file},
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract message data
    result = bot.check_message_type()

    # Check message data values
    assert "voice" in result.keys()
    assert expected_file == result["voice"]

def test_telegrambot_check_message_type_video(requests_mock):
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
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "video": {"file_id": expected_file},
                    "caption": expected_caption,
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

    # Extract the message data
    result = bot.check_message_type()

    # Check message data values
    assert "video" in result.keys()
    assert expected_file == result["video"][0]
    assert expected_caption == result["video"][1]

def test_telegrambot_check_message_type_none(requests_mock):
    """
    Test to check detection of invalid format
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # Mocking response of /getUpdates post request with
    # expected values previously defined
    mock_response = {
        "result": [
            {
                "message": {
                    "message_id": 80,
                    "chat": {"id": 12345},
                    "other": {"file_id": "other_file"},
                }
            }
        ]
    }
    requests_mock.post(f"{bot.url}getUpdates", json=mock_response)

    # Update message info
    bot.check_new_message()

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
        result = bot._download_file(file_id=1234)

        # Check the properly call to wget download function
        # and the correct result of _download_file bot method
        mock_download.assert_called_once()
        assert result

def test_telegrambot_get_file_wrong_folder():
    """
    Test to check get file method in case of wrong folder configured
    """

    # Initialize TelegramBot passing the testing configuration file
    data = telegrambot.read_config_file("test/config.toml")
    bot = telegrambot.TelegramBot(data)

    # This folder doesn't exist, so the _download_file method
    # detects this point and return a False flag
    target_folder = "wrong_download_folder/"

    assert not bot._download_file(file_id=1234,
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

    assert not bot._download_file(file_id=1234,
                                  download_path=target_folder)

# def test_telegrambot_get_file(requests_mock):
#     """
#     Test to check file method behaviour
#     """

#     data = telegrambot.read_config_file("test/config.toml")
#     bot = telegrambot.TelegramBot(data)

#     mock_response = {
#         "ok": 200,
#         "result": {
#             "file_path": "download/"
#         }
#     }
#     requests_mock.post(f"{bot.url}file", json=mock_response)

#     with pytest.raises(urllib.error.HTTPError):
#         bot._download_file(file_id=1234)

# def test_telegrambot_download_file(requests_mock):
#     """
#     Test to check file method behaviour with a wrong folder path
#     """

#     data = {'API_KEY': 'valid_api_key'}
#     bot = telegrambot.TelegramBot(data)

#     file_id = "123456789"
#     download_path = "downloads/"

#     mock_response = {
#         "ok": 200,
#         "result": {
#             "file_path": download_path
#         }
#     }
#     requests_mock.post(f"{bot.url}file", json=mock_response)

#     if not os.path.isdir(download_path):
#         os.mkdir(download_path)
#     assert bot._download_file(file_id, download_path)

# def test_telegrambot_get_file_wrong_folder(requests_mock):
#     """
#     Test to check file method behaviour with a wrong folder path
#     """

#     data = {'API_KEY': 'valid_api_key'}
#     bot = telegrambot.TelegramBot(data)

#     file_id = "123456789"
#     download_path = "downloads/"

#     mock_response = {
#         "ok": 200,
#         "result": {
#             "file_path": "download/"
#         }
#     }
#     requests_mock.post(f"{bot.url}file", json=mock_response)

#     assert bot._download_file(file_id, download_path)
