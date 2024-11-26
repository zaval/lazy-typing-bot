import logging
import os

from fastapi import FastAPI, Request
from telegram import Update, File
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from google.cloud import storage

logger = logging.getLogger(__name__)
app = FastAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    authorized_users = os.getenv("AUTHORIZED_USERS", "").split(",")
    if str(user.id) not in authorized_users:
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot."
        )
        return
    await update.message.reply_text(
        "Hi! I'm Lazy Typing Bot, I will help you to transcribe voice messages from the lazy people. "
        "No more need to listen that \"um\", \"ah\", chewing, etc. Just usefully information.\n"
        "Let's get started! Send or forward to me a voice message or audio file and I will transcribe it for you."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Send a voice message or audio file and I will transcribe it for you."
    )

async def attachment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    if update.message.effective_attachment:
        await update.message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)
        attachment = update.message.effective_attachment
        new_file: File = await attachment.get_file()
        mime_type = attachment.mime_type
        file_extension = mime_type.split('/')[-1] if mime_type else ''

        buffer = await new_file.download_as_bytearray()

        storage_client = storage.Client()
        bucket = storage_client.bucket(os.getenv("BUCKET_NAME"))
        blob = bucket.blob(f"inputs/{update.effective_user.id}/{attachment.file_id}.{file_extension}")

        blob.upload_from_string(bytes(buffer), content_type=mime_type)
        await update.message.reply_chat_action(ChatAction.TYPING)

@app.post("/tg")
async def tg(request: Request):

    if os.getenv("TG_SECRET") and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("TG_SECRET"):
        return {"message": "Unauthorized"}

    application = Application.builder().token(os.getenv("TG_TOKEN")).updater(None).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(
            (filters.VOICE | filters.AUDIO | filters.FORWARDED) & ~filters.COMMAND,
            attachment
        )
    )

    async with application:
        await application.process_update(
            Update.de_json(data=await request.json(), bot=application.bot)
        )

    return {"message": "OK"}
