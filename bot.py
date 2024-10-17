import requests
import zipfile
import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import time

# Bot Configuration
TELEGRAM_TOKEN = '7317428432:AAGrzU7doIFs7tnmm1lpTJa7r9-9Y_1sHh0'
CHANNEL_ID = '@iptestcf'
FILE_URL = 'https://zip.baipiao.eu.org'

bot = Bot(token=TELEGRAM_TOKEN)

async def download_and_extract_zip():
    try:
        # Download the ZIP file
        response = requests.get(FILE_URL)
        if response.status_code == 200:
            zip_file_name = 'downloaded_file.zip'
            with open(zip_file_name, 'wb') as f:
                f.write(response.content)

            # Extract the ZIP file
            extract_dir = 'extracted_files'
            with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Send extracted files to the Telegram channel
            for root, dirs, files in os.walk(extract_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'rb') as f:
                        try:
                            await bot.send_document(chat_id=CHANNEL_ID, document=f)
                            print(f"File {file_name} sent successfully")
                            # Add a delay to avoid rate limits
                            time.sleep(3)  # adjust this delay if necessary
                        except TelegramError as e:
                            print(f"Failed to send file: {e}")
                            if "Flood control exceeded" in str(e):
                                print("Waiting for 60 seconds to avoid flood control...")
                                time.sleep(60)  # wait longer to bypass flood control
                            continue

            # Cleanup
            os.remove(zip_file_name)
            for root, dirs, files in os.walk(extract_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(extract_dir)

        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    except TelegramError as e:
        print(f"Failed to send file: {e}")

async def main():
    await download_and_extract_zip()

    # Schedule to run every 24 hours
    while True:
        await asyncio.sleep(86400)  # 86400 detik = 24 jam
        await download_and_extract_zip()

if __name__ == "__main__":
    asyncio.run(main())