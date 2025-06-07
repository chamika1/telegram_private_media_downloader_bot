# Telegram Media Downloader Bot

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges here if needed, e.g., build status, coverage -->

A Telegram bot that allows you to download media (photos, videos) from Telegram channels and groups by simply sending message links.

## Features

- Download photos and videos from Telegram channels/groups
- Works with both public and private channels (that you have access to)
- Simple to use - just send a Telegram message link
- Supports various media formats

## Requirements

- Python 3.7+
- Telegram API credentials (API ID and API Hash)
- Telegram Bot Token

## Installation & Setup

1.  **Clone the repository:**
    If you have git installed:
    ```bash
    git clone <URL_OF_YOUR_REPOSITORY> # Replace with your actual repository URL
    cd <YOUR_PROJECT_DIRECTORY_NAME>   # Replace with your project's directory name
    ```
    Alternatively, download the source code ZIP file from your repository and extract it.

2.  **Create and configure `config.ini`:**
    In the project's root directory, create a file named `config.ini`. Add your Telegram API credentials and bot token to this file. It should look like this:
    ```ini
    [Telegram]
    api_id = YOUR_API_ID
    api_hash = YOUR_API_HASH
    bot_token = YOUR_BOT_TOKEN
    ```
    Replace `YOUR_API_ID`, `YOUR_API_HASH`, and `YOUR_BOT_TOKEN` with your actual credentials.
    -   You can obtain `api_id` and `api_hash` from [my.telegram.org/apps](https://my.telegram.org/apps).
    -   You can obtain your `bot_token` by creating a new bot with @BotFather on Telegram.

3.  **Install dependencies:**
    Navigate to the project directory in your terminal and install the required Python packages using:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Authenticate your Telethon session:**
    Run the `auth.py` script to authorize the bot with your Telegram account. This script uses Telethon to log in and will create a `telemedia_session.session` file.
    ```bash
    python auth.py
    ```
    You will be prompted to enter your phone number and the login code sent to your Telegram account. This step is crucial for the bot to access media, especially from private channels or groups you are a member of.

## Usage

1.  **Start the bot:**
    Once the setup is complete, run the main bot script:
    ```bash
    python bot.py
    ```
    The bot will start polling for updates.

2.  **Interact with the bot on Telegram:**
    - Open a chat with your bot on Telegram.
    - You can send `/start` to see a welcome message and `/help` for assistance.
    - Send a direct link to a Telegram message that contains a photo or video you wish to download (e.g., `https://t.me/c/channel_id/message_id` or `https://t.me/username/message_id`).
    - The bot will process the link, download the media, and send it back to you in the chat.

## License

This project is licensed under the MIT License. You can find more details in the `LICENSE` file if you choose to add one.
<!-- If you add a LICENSE file, you can change the above line to:
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
-->
