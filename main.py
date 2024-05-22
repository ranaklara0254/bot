import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

# Replace these with your own values
API_ID = '5310709'
API_HASH = '63a546bdaf18e2cbba99f87b4274fa05'
BOT_TOKEN = '5436508081:AAEaiqF2JxmFf3RLZtybQh0QzqvOSVtyLYA'

# Directory to save downloaded files
DOWNLOAD_DIR = 'downloads'

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Initialize the bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text('Hi! Send me a file and I will download it with progress updates.')

async def progress(current, total, message: Message, start_time):
    # Calculate progress percentage
    percentage = current * 100 / total

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Calculate download speed
    speed = current / elapsed_time

    # Estimate remaining time
    remaining_time = (total - current) / speed

    # Create progress message
    progress_message = (
        f"Downloaded: {current / 1024 / 1024:.2f}MB/{total / 1024 / 1024:.2f}MB "
        f"({percentage:.2f}%)\n"
        f"Speed: {speed / 1024:.2f} KB/s\n"
        f"Estimated time remaining: {remaining_time:.2f} seconds"
    )

    try:
        # Edit the message with progress update
        await message.edit(progress_message)
    except FloodWait as e:
        # Handle rate limit exception
        time.sleep(e.value)

@app.on_message(filters.document)
async def download_file(client, message):
    try:
        file_name = message.document.file_name
        download_path = os.path.join(DOWNLOAD_DIR, file_name)

        # Send initial message to user
        progress_message = await message.reply_text("Starting download...")

        # Start time for calculating speed and ETA
        start_time = time.time()

        # Download file with progress callback
        await client.download_media(
            message=message.document,
            file_name=download_path,
            progress=progress,
            progress_args=(progress_message, start_time)
        )

        await progress_message.edit(f'File {file_name} has been downloaded to {download_path}')

        # Upload the downloaded file to bashupload.com
        files = {'file': open(download_path, 'rb')}
        response = requests.post('https://bashupload.com/', files=files)

        # Send the response back to the user
        await message.reply_text(f'Upload response: {response.text}')
    except Exception as e:
        await message.reply_text(f'An error occurred: {e}')

app.run()
