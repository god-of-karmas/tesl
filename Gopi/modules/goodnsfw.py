import os
import html
import nekos
import requests
from PIL import Image
from time import sleep

import Gopi.modules.sql.nsfw_sql as sql
from Gopi import dispatcher
from Gopi.modules.log_channel import gloggable
from Gopi.modules.helper_funcs.filters import CustomFilters
from Gopi.modules.helper_funcs.chat_status import user_admin

from telegram import Update
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import CommandHandler, CallbackContext
from telegram.utils.helpers import mention_html


@user_admin
@gloggable
def add_nsfw(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user  # Remodified by @EverythingSuckz
    is_nsfw = sql.is_nsfw(chat.id)
    if not is_nsfw:
        sql.set_nsfw(chat.id)
        msg.reply_text("Activated NSFW Mode!")
        message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ACTIVATED_NSFW\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        )
        return message
    else:
        msg.reply_text("NSFW Mode is already Activated for this chat!")
        return ""


@user_admin
@gloggable
def rem_nsfw(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    is_nsfw = sql.is_nsfw(chat.id)
    if not is_nsfw:
        msg.reply_text("NSFW Mode is already Deactivated")
        return ""
    else:
        sql.rem_nsfw(chat.id)
        msg.reply_text("Rolled Back to SFW Mode!")
        message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"DEACTIVATED_NSFW\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        )
        return message


def list_nsfw_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_nsfw_chats()
    text = "<b>NSFW Activated Chats</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title if x.title else x.first_name
            text += f"• <code>{name}</code>\n"
        except BadRequest:
            sql.rem_nsfw(*chat)
        except Unauthorized:
            sql.rem_nsfw(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")


def neko(update, context):
    msg = update.effective_message
    target = "neko"
    msg.reply_photo(nekos.img(target))


def wallpaper(update, context):
    msg = update.effective_message
    target = "wallpaper"
    msg.reply_photo(nekos.img(target))


def ngif(update, context):
    chat_id = update.effective_chat.id
    if not update.effective_message.chat.type == "private":
        is_nsfw = sql.is_nsfw(chat_id)
        if not is_nsfw:
            return
    msg = update.effective_message
    target = "ngif"
    msg.reply_video(nekos.img(target))


def feed(update, context):
    msg = update.effective_message
    target = "feed"
    msg.reply_video(nekos.img(target))


def kemonomimi(update, context):
    chat_id = update.effective_chat.id
    if not update.effective_message.chat.type == "private":
        is_nsfw = sql.is_nsfw(chat_id)
        if not is_nsfw:
            return
    msg = update.effective_message
    target = "kemonomimi"
    msg.reply_photo(nekos.img(target))


def gasm(update, context):
    chat_id = update.effective_chat.id
    if not update.effective_message.chat.type == "private":
        is_nsfw = sql.is_nsfw(chat_id)
        if not is_nsfw:
            return
    msg = update.effective_message
    target = "gasm"
    with open("temp.png", "wb") as f:
        f.write(requests.get(nekos.img(target)).content)
    img = Image.open("temp.png")
    img.save("temp.webp", "webp")
    msg.reply_document(open("temp.webp", "rb"))
    os.remove("temp.webp")


def poke(update, context):
    msg = update.effective_message
    target = "poke"
    msg.reply_video(nekos.img(target))


def holo(update, context):
    msg = update.effective_message
    target = "holo"
    msg.reply_photo(nekos.img(target))


def smug(update, context):
    msg = update.effective_message
    target = "smug"
    msg.reply_video(nekos.img(target))


def baka(update, context):
    msg = update.effective_message
    target = "baka"
    msg.reply_video(nekos.img(target))


ADD_NSFW_HANDLER = CommandHandler("addnsfw", add_nsfw, run_async=True)
REMOVE_NSFW_HANDLER = CommandHandler("rmnsfw", rem_nsfw, run_async=True)
LIST_NSFW_CHATS_HANDLER = CommandHandler(
    "nsfwchats", list_nsfw_chats, filters=CustomFilters.dev_filter, run_async=True
)
NEKO_HANDLER = CommandHandler("neko", neko, run_async=True)
WALLPAPER_HANDLER = CommandHandler("wallpaper", wallpaper, run_async=True)
NGIF_HANDLER = CommandHandler("ngif", ngif, run_async=True)
FEED_HANDLER = CommandHandler("feed", feed, run_async=True)
KEMONOMIMI_HANDLER = CommandHandler("kemonomimi", kemonomimi, run_async=True)
GASM_HANDLER = CommandHandler("gasm", gasm, run_async=True)
POKE_HANDLER = CommandHandler("poke", poke, run_async=True)
HOLO_HANDLER = CommandHandler("holo", holo, run_async=True)
SMUG_HANDLER = CommandHandler("smug", smug, run_async=True)
BAKA_HANDLER = CommandHandler("baka", baka, run_async=True)


dispatcher.add_handler(ADD_NSFW_HANDLER)
dispatcher.add_handler(REMOVE_NSFW_HANDLER)
dispatcher.add_handler(LIST_NSFW_CHATS_HANDLER)
dispatcher.add_handler(NEKO_HANDLER)
dispatcher.add_handler(WALLPAPER_HANDLER)
dispatcher.add_handler(NGIF_HANDLER)
dispatcher.add_handler(FEED_HANDLER)
dispatcher.add_handler(KEMONOMIMI_HANDLER)
dispatcher.add_handler(GASM_HANDLER)
dispatcher.add_handler(POKE_HANDLER)
dispatcher.add_handler(HOLO_HANDLER)
dispatcher.add_handler(SMUG_HANDLER)
dispatcher.add_handler(BAKA_HANDLER)

__handlers__ = [
    ADD_NSFW_HANDLER,
    REMOVE_NSFW_HANDLER,
    LIST_NSFW_CHATS_HANDLER,
    NEKO_HANDLER,
    WALLPAPER_HANDLER,
    NGIF_HANDLER,
    FEED_HANDLER,
    KEMONOMIMI_HANDLER,
    GASM_HANDLER,
    POKE_HANDLER,
    HOLO_HANDLER,
    SMUG_HANDLER,
    BAKA_HANDLER,
]

__help__ = """
Usage:
    
/addnsfw : Enable NSFW mode
/rmnsfw : Disable NSFW mode
 
Commands :   
 - /neko: Sends Random SFW Neko source Images.
 - /ngif: Sends Random Neko GIFs.
 - /wallpaper get wonderfull anime wallpapers.
 - /feed: Sends Random Feeding GIFs.
 - /kemonomimi: Sends Random KemonoMimi source Images.
 - /gasm: Sends Random Orgasm Stickers.
 - /poke: Sends Random Poke GIFs.
 - /holo: Sends Random Holo source Images.
 - /baka: Sends Random Baka Shout GIFs.
"""

__mod_name__ = "🐰 AɴɪᴍᴇPG & NSFW"
