# Integrated Traditional Chatbot with Azure AI Language Service

## Overview

This project extends a simple echo bot (from the Microsoft Bot Framework SDK)
by integrating **Azure AI Language** for sentiment analysis. The chatbot analyzes
the sentiment of user messages and responds with context-aware replies based on
whether the input is positive, negative, neutral, or mixed.

## Origin

The base echo bot code was adapted from the
[Microsoft Bot Framework Python SDK samples](https://github.com/microsoft/BotBuilder-Samples/tree/main/samples/python/02.echo-bot).
It has been extended with Azure AI Text Analytics integration for the
MSAI-631 course at the University of the Cumberlands.

## Features

- **Sentiment Analysis**: Analyzes user messages using Azure AI Language and
  responds based on detected sentiment (positive, negative, neutral, mixed).
- **Capabilities Listing**: Type `help` or `capabilities` to see what the bot
  can do.
- **Keyword Detection**: Recognizes greetings, farewells, and specific commands.
- **Error Handling**: Gracefully handles malformed input, empty messages, and
  API errors.
- **Confidence Scores**: Reports sentiment confidence percentages for
  transparency.

## Prerequisites

- Python 3.9 or later
- An Azure account with an AI Language resource provisioned
- Bot Framework Emulator (for local testing)

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/dpadala541/integrated-chatbot.git
   cd integrated-chatbot
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** with your Azure AI Language keys:

   ```bash
   # Windows
   SET MicrosoftAPIKey=<your-key-here>
   SET MicrosoftAIServiceEndpoint=<your-endpoint-here>

   # macOS/Linux
   export MicrosoftAPIKey=<your-key-here>
   export MicrosoftAIServiceEndpoint=<your-endpoint-here>
   ```

4. **Run the bot**:

   ```bash
   python app.py
   ```

5. **Test with Bot Framework Emulator**:

   Open the emulator and connect to `http://localhost:3978/api/messages`.

## Project Structure

```
integrated-chatbot/
├── app.py              # Application entry point and web server
├── bot.py              # Bot logic with sentiment analysis integration
├── config.py           # Configuration (keys, endpoints, port)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── tests/
    └── test_bot.py     # Unit tests for the bot
```

## Commands

| Command                  | Description                              |
| ------------------------ | ---------------------------------------- |
| `help` or `capabilities` | Lists the bot's features                 |
| `hello` / `hi`           | Greets the user                          |
| `bye` / `goodbye`        | Says farewell                            |
| `about`                  | Shows information about the bot          |
| Any other text           | Performs sentiment analysis on the input  |

## AI Disclosure

Claude (Anthropic) was used to assist in developing the source code and
drafting the project report. All code was reviewed, tested, and understood
by the author before submission.

## Author

Dheeraj Padala  
University of the Cumberlands  
MSAI-631: Artificial Intelligence for Human-Computer Interaction
