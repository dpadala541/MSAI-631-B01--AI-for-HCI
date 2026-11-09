#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Integrated chatbot that extends the echo bot with Azure AI Language
sentiment analysis.

Origin: Adapted from the Microsoft Bot Framework echo-bot sample
(https://github.com/microsoft/BotBuilder-Samples).
Modified for MSAI-631 to demonstrate AI-as-a-Service integration.
"""

import logging
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)


class IntegratedBot(ActivityHandler):
    """A chatbot that performs sentiment analysis on user messages using
    Azure AI Language and responds with contextual feedback."""

    # Keyword sets for simple command matching
    GREETINGS = {"hello", "hi", "hey", "greetings", "howdy"}
    FAREWELLS = {"bye", "goodbye", "exit", "quit", "see you"}
    HELP_COMMANDS = {"help", "capabilities", "commands", "what can you do"}

    def __init__(self, api_key: str, endpoint: str):
        """Initialize the bot with Azure AI Language credentials.

        Args:
            api_key: Azure AI Language API key.
            endpoint: Azure AI Language endpoint URL.
        """
        super().__init__()
        self.api_key = api_key
        self.endpoint = endpoint
        self.client = None

        # Only create the client if credentials are provided
        if api_key and endpoint:
            try:
                credential = AzureKeyCredential(api_key)
                self.client = TextAnalyticsClient(
                    endpoint=endpoint, credential=credential
                )
                logger.info("Azure AI Language client initialized successfully.")
            except Exception as exc:
                logger.error("Failed to initialize Azure AI client: %s", exc)
        else:
            logger.warning(
                "Azure AI credentials not set. Sentiment analysis disabled."
            )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """Greet new members when they join the conversation."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome = (
                    "Welcome! I am the **Integrated AI Chatbot**.\n\n"
                    "I can analyze the sentiment of your messages using "
                    "Azure AI Language.\n\n"
                    "Type **help** to see my full list of capabilities."
                )
                await turn_context.send_activity(welcome)

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages from the user."""
        user_text = (turn_context.activity.text or "").strip()

        # Handle empty or whitespace-only messages
        if not user_text:
            await turn_context.send_activity(
                "It looks like you sent an empty message. "
                "Please type something and I will analyze it!"
            )
            return

        normalized = user_text.lower()

        # Check for commands first
        if normalized in self.HELP_COMMANDS:
            await self._send_capabilities(turn_context)
        elif normalized in self.GREETINGS:
            await turn_context.send_activity(
                f"Hello! Nice to meet you. How can I help you today?\n\n"
                f"Type **help** to see what I can do."
            )
        elif normalized in self.FAREWELLS:
            await turn_context.send_activity(
                "Goodbye! It was great chatting with you. Have a wonderful day!"
            )
        elif normalized == "about":
            await self._send_about(turn_context)
        else:
            # Perform sentiment analysis on all other input
            await self._analyze_sentiment(turn_context, user_text)

    # ------------------------------------------------------------------
    # Command responses
    # ------------------------------------------------------------------

    async def _send_capabilities(self, turn_context: TurnContext):
        """Send a list of the bot's capabilities."""
        capabilities = (
            "Here are my capabilities:\n\n"
            "1. **Sentiment Analysis** - Send me any text and I will "
            "analyze whether it is positive, negative, neutral, or mixed.\n\n"
            "2. **Greetings** - Say *hello*, *hi*, or *hey* to start a "
            "conversation.\n\n"
            "3. **Farewell** - Say *bye* or *goodbye* to end our chat.\n\n"
            "4. **About** - Type *about* to learn more about this bot.\n\n"
            "5. **Help** - Type *help* or *capabilities* to see this list "
            "again.\n\n"
            "Try typing a sentence and I will tell you what sentiment "
            "I detect!"
        )
        await turn_context.send_activity(capabilities)

    async def _send_about(self, turn_context: TurnContext):
        """Send information about the bot."""
        about = (
            "**Integrated AI Chatbot**\n\n"
            "This bot was built using the Microsoft Bot Framework SDK "
            "and integrates Azure AI Language for sentiment analysis.\n\n"
            "**Course**: MSAI-631 - AI for Human-Computer Interaction\n"
            "**University**: University of the Cumberlands\n"
            "**Author**: Dheeraj Padala\n\n"
            "The bot demonstrates how traditional chatbots can be "
            "enhanced with cloud-based AI services."
        )
        await turn_context.send_activity(about)

    # ------------------------------------------------------------------
    # Sentiment analysis
    # ------------------------------------------------------------------

    async def _analyze_sentiment(
        self, turn_context: TurnContext, text: str
    ):
        """Analyze the sentiment of the user's message and respond.

        Args:
            turn_context: The current conversation turn.
            text: The user's message text.
        """
        if not self.client:
            await turn_context.send_activity(
                "Sentiment analysis is currently unavailable. "
                "Please ensure the Azure AI Language credentials are "
                "configured correctly."
            )
            return

        try:
            # Call Azure AI Language for sentiment analysis
            response = self.client.analyze_sentiment(documents=[text])
            result = response[0]

            if result.is_error:
                logger.error(
                    "Sentiment analysis error: %s - %s",
                    result.id, result.error.message,
                )
                await turn_context.send_activity(
                    "I encountered an error analyzing your message. "
                    "Please try rephrasing it."
                )
                return

            # Build a response based on the sentiment
            sentiment = result.sentiment
            confidence = result.confidence_scores
            reply = self._build_sentiment_response(
                text, sentiment, confidence
            )
            await turn_context.send_activity(reply)

        except Exception as exc:
            logger.error("Sentiment analysis failed: %s", exc)
            await turn_context.send_activity(
                "Something went wrong while analyzing your message. "
                "Please try again later."
            )

    def _build_sentiment_response(
        self, text: str, sentiment: str, confidence
    ) -> str:
        """Create a human-friendly response from sentiment results.

        Args:
            text: The original user message.
            sentiment: The detected sentiment label.
            confidence: Confidence scores for each sentiment category.

        Returns:
            A formatted response string.
        """
        # Emoji and contextual phrasing for each sentiment
        sentiment_map = {
            "positive": {
                "emoji": "😊",
                "response": "That sounds great! I am glad to hear something positive.",
            },
            "negative": {
                "emoji": "😔",
                "response": "I am sorry to hear that. I hope things get better.",
            },
            "neutral": {
                "emoji": "😐",
                "response": "That seems like a neutral statement.",
            },
            "mixed": {
                "emoji": "🤔",
                "response": "Your message has mixed sentiments. It contains both positive and negative elements.",
            },
        }

        info = sentiment_map.get(sentiment, sentiment_map["neutral"])

        # Format confidence scores as percentages
        pos_pct = f"{confidence.positive * 100:.1f}%"
        neg_pct = f"{confidence.negative * 100:.1f}%"
        neu_pct = f"{confidence.neutral * 100:.1f}%"

        reply = (
            f"**Sentiment Analysis Result** {info['emoji']}\n\n"
            f"Your message: *\"{text}\"*\n\n"
            f"**Detected Sentiment**: {sentiment.capitalize()}\n\n"
            f"**Confidence Scores**:\n"
            f"- Positive: {pos_pct}\n"
            f"- Negative: {neg_pct}\n"
            f"- Neutral: {neu_pct}\n\n"
            f"{info['response']}"
        )
        return reply
