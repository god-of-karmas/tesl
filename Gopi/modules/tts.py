import html
import re
from datetime import datetime
from typing import List
import random
from telegram import ChatAction
from gtts import gTTS
import time
from Gopi import dispatcher
from Gopi.modules.disable import DisableAbleCommandHandler
from telegram import Update, ChatAction
from telegram.ext import CallbackContext


def tts(update: Update, context: CallbackContext):
    args = context.args
    reply = " ".join(args)
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    lang = "ml"
    tts = gTTS(reply, lang)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "en"
        tts = gTTS(reply, lang)
        tts.save("k.mp3")
    with open("k.mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)


TTS_HANDLER = DisableAbleCommandHandler("tts", tts, pass_args=True, run_async=True)
dispatcher.add_handler(TTS_HANDLER)

__mod_name__ = "🗣️ ᴛᴛs"
__command_list__ = ["tts"]
__handlers__ = [TTS_HANDLER]
