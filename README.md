[![TelegramBot Workflow](https://github.com/ocriado91/python-telegrambot/actions/workflows/python.yaml/badge.svg)](https://github.com/ocriado91/python-telegrambot/actions/workflows/python.yaml)
[![codecov](https://codecov.io/gh/ocriado91/python-telegrambot/graph/badge.svg?token=BM1U5IQKZS)](https://codecov.io/gh/ocriado91/python-telegrambot)

<p align="center">
  <img src="https://github.com/ocriado91/python-telegrambot/assets/55914877/5c5b87e5-487e-428d-bc8f-647c795efbe6" width="200px"/>
</p>


# python-telegrambot
This module provides an interface for `TelegramBot API` (https://core.telegram.org/bots/api)

## Telegram Bot
Bots are small applications that use messages for a interface based into following
a common pattern:

`https://api.telegram.org/bot<token>/METHOD_NAME`

where:

* Token: a unique ID given at the moment of the Bot creation
* METHOD_NAME: According with the desired action to applly, we need to call to
the correspond method.

## Actions
In this project, we support the following actions:
1. Send and receive messages
2. Send and receive pictures
3. Send and receive audios
4. Send and receive videos

Being the architecture diagram of sending actions:

<p align="center">
  <img src="images/telegrambot_send.drawio.png"/>
</p>
and for receiving actions:

<p align="center">
  <img src="images/telegrambot_send.drawio.png"/>
</p>
