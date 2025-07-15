# GPT Consultant for Business

This project is a Telegram bot designed to assist businesses by providing consulting services powered by OpenAI's GPT-4 model. The bot is built using the aiogram framework and integrates with the OpenAI API to handle user queries and provide context-aware responses.

## Features

- Context loading and management
- Command handling, including `/setcontext` to customize the bot's behavior
- Message processing to generate responses using the OpenAI API
- Conversation history storage in an SQLite database

## Project Structure

```
gpt_consultant_for_business
├── src
│   ├── main.py               # Entry point of the bot
│   ├── config.py             # Configuration settings
│   ├── handlers               # Command and message handlers
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   └── messages.py
│   ├── utils                  # Utility functions and classes
│   │   ├── __init__.py
│   │   ├── context_loader.py
│   │   ├── db.py
│   │   └── openai_api.py
│   └── models                 # Data models
│       ├── __init__.py
│       └── history.py
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Требования
- Python 3.12+
- Все зависимости из requirements.txt

## Installation

1. Clone the repository:
   ```