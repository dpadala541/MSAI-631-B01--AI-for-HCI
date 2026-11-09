#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Application entry point for the Integrated AI Chatbot.

This module creates the web server, initializes the Bot Framework adapter,
and connects the IntegratedBot (with Azure AI Language integration) to the
messaging endpoint.

Origin: Adapted from the Microsoft Bot Framework echo-bot sample.
Modified for MSAI-631 to add Azure AI Language sentiment analysis.
"""

import sys
import traceback
from datetime import datetime
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from bot import IntegratedBot

# Load configuration
CONFIG = DefaultConfig()

# Create adapter
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Error handler
async def on_error(context: TurnContext, error: Exception):
    """Catch-all error handler for the bot adapter.

    Logs the error and sends a user-friendly message so the conversation
    can continue.
    """
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity(
        "The bot encountered an error. Please try again."
    )
    # Send a trace activity for the Bot Framework Emulator
    await context.send_activity(
        Activity(
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
            label="TurnError",
        )
    )


ADAPTER.on_turn_error = on_error

# Create the bot with Azure AI Language credentials
BOT = IntegratedBot(api_key=CONFIG.API_KEY, endpoint=CONFIG.ENDPOINT_URI)


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    """Main endpoint for Bot Framework messages.

    Receives incoming activities from the Bot Framework channel and
    routes them to the bot for processing.
    """
    # Verify content type
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


def init_func(argv):
    """Initialize the aiohttp web application."""
    app = web.Application(middlewares=[aiohttp_error_middleware])
    app.router.add_post("/api/messages", messages)
    return app


if __name__ == "__main__":
    APP = init_func(None)

    try:
        print(f"Bot started on port {CONFIG.PORT}")
        print(f"Endpoint: http://localhost:{CONFIG.PORT}/api/messages")
        print(f"Azure AI Endpoint: {CONFIG.ENDPOINT_URI or '(not set)'}")
        print(f"API Key: {'***configured***' if CONFIG.API_KEY else '(not set)'}")
        print("Press Ctrl+C to stop the bot.\n")

        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
