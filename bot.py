import logging
import os
from telegram import Update, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from urllib.parse import urlparse

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hi! Send me a .txt file containing video and PDF URLs, and I'll create an HTML message with those links."
    )

async def handle_text_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded .txt files containing URLs."""
    if update.message.document:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name

        if file_name.endswith(".txt"):
            file_path = await file.download_to_drive(f"temp_{file_name}")
            
            try:
                with open(file_path, "r") as f:
                    urls = [line.strip() for line in f if line.strip()]

                if not urls:
                    await update.message.reply_text("The .txt file is empty.")
                    return

                html_content = "<h2>Links from your file</h2><ul>"
                for url in urls:
                    parsed_url = urlparse

(url)
                    file_name = os.path.basename(parsed_url.path)
                    if url.lower().endswith((".mp4", ".mkv", ".avi", ".mov")):
                        html_content += (
                            f'<li><strong>{file_name}</strong><br>'
                            f'<video width="320" height="240" controls>'
                            f'<source src="{url}" type="video/mp4">'
                            f'Your browser does not support the video tag.'
                            f'</video></li>'
                        )
                    elif url.lower().endswith(".pdf"):
                        html_content += (
                            f'<li><strong>{file_name}</strong><br>'
                            f'<a href="{url}" target="_blank">View PDF</a></li>'
                        )
                    else:
                        html_content += (
                            f'<li><strong>{file_name}</strong><br>'
                            f'<a href="{url}" target="_blank">{url}</a></li>'
                        )
                html_content += "</ul>"

                await update.message.reply_text(
                    html_content, parse_mode=ParseMode.HTML
                )

            except Exception as e:
                logger.error(f"Error processing file: {e}")
                await update.message.reply_text(
                    "An error occurred while processing the file. Please ensure it contains valid URLs."
                )
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            await update.message.reply_text("Please upload a .txt file.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

async def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_text_file))
    application.add_error_handler(error_handler)

    port = int(os.environ.get("PORT", 8443))
    webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
