import asyncio
from telethon import TelegramClient
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Telegram API credentials
API_ID = config['Telegram']['api_id']
API_HASH = config['Telegram']['api_hash']

async def main():
    # Create the client and connect
    client = TelegramClient('telemedia_session', API_ID, API_HASH)
    await client.start()
    
    # Ensure you're authorized
    if not await client.is_user_authorized():
        print("You need to login first!")
        await client.send_code_request(input("Enter your phone number: "))
        await client.sign_in(code=input("Enter the code you received: "))
    
    print("Authorization successful!")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())