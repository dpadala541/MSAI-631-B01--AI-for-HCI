#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Configuration for the Integrated Chatbot.

Reads the bot port, Azure AI Language API key, and endpoint from
environment variables so that sensitive credentials are never
hard-coded in the source.
"""

import os


class DefaultConfig:
    """Bot configuration sourced from environment variables."""

    # ---------- Bot Framework ----------
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # ---------- Azure AI Language Service ----------
    # Set these before running:
    #   SET MicrosoftAPIKey=<your-key>
    #   SET MicrosoftAIServiceEndpoint=<your-endpoint>
    API_KEY = os.environ.get("MicrosoftAPIKey", "")
    ENDPOINT_URI = os.environ.get("MicrosoftAIServiceEndpoint", "")
