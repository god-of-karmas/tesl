import os
import math
import io

import urllib.request as urllib
from cloudscraper import CloudScraper
from urllib.parse import quote as urlquote
from urllib.error import HTTPError
from PIL import Image
from html import escape
from bs4 import BeautifulSoup as bs

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import TelegramError, Update
from telegram.ext import run_async, CallbackContext
from telegram.utils.helpers import mention_html

from Gopi import dispatcher
from Gopi.modules.disable import DisableAbleCommandHandler

combot_stickers_url = "https://combot.org/telegram/stickers?q="

scraper = CloudScraper()


def stickerid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            parse_mode=ParseMode.HTML,
        )


def get_cbs_data(query, page, user_id):
    # returns (text, buttons)
    text = scraper.get(f"{combot_stickers_url}{urlquote(query)}&page={page}").text
    soup = bs(text, "lxml")
    div = soup.find("div", class_="page__container")
    packs = div.find_all("a", class_="sticker-pack__btn")
    titles = div.find_all("div", "sticker-pack__title")
    has_prev_page = has_next_page = None
    highlighted_page = div.find("a", class_="pagination__link is-active")
    if highlighted_page is not None and user_id is not None:
        highlighted_page = highlighted_page.parent
        has_prev_page = highlighted_page.previous_sibling.previous_sibling is not None
        has_next_page = highlighted_page.next_sibling.next_sibling is not None
    buttons = []
    if has_prev_page:
        buttons.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"cbs_{page - 1}_{user_id}")
        )
    if has_next_page:
        buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=f"cbs_{page + 1}_{user_id}")
        )
    buttons = InlineKeyboardMarkup([buttons]) if buttons else None
    text = f"Stickers for <code>{escape(query)}</code>:\nPage: {page}"
    if packs and titles:
        for pack, title in zip(packs, titles):
            link = pack["href"]
            text += f"\n• <a href='{link}'>{escape(title.get_text())}</a>"
    elif page == 1:
        text = "No results found, try a different term"
    else:
        text += "\n\nInterestingly, there's nothing here."
    return text, buttons


def cb_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    query = " ".join(msg.text.split()[1:])
    if not query:
        msg.reply_text("Provide some name to search for pack.")
        return
    if len(query) > 50:
        msg.reply_text("Provide a search query under 50 characters")
        return
    if msg.from_user:
        user_id = msg.from_user.id
    else:
        user_id = None
    text, buttons = get_cbs_data(query, 1, user_id)
    msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)


def cbs_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, page, user_id = query.data.split("_", 2)
    if int(user_id) != query.from_user.id:
        query.answer("Not for you", cache_time=60 * 60)
        return
    search_query = query.message.text.split("\n", 1)[0].split(maxsplit=2)[2][:-1]
    text, buttons = get_cbs_data(search_query, int(page), query.from_user.id)
    query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)
    query.answer()


def getsticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id

    if msg.reply_to_message and msg.reply_to_message.sticker:
        animated = msg.reply_to_message.sticker.is_animated == True
        videos = msg.reply_to_message.sticker.is_video == True

        if not animated and not videos:
            file_id = msg.reply_to_message.sticker.file_id
            new_file = bot.get_file(file_id)
            new_file.download("sticker.png")
            bot.sendDocument(chat_id, document=open("sticker.png", "rb"))
            bot.sendChatAction(chat_id, "upload_photo")
            bot.sendPhoto(chat_id, photo=open("sticker.png", "rb"))
            os.remove("sticker.png")
        elif animated:
            file_id = msg.reply_to_message.sticker.file_id
            new_file = bot.get_file(file_id)
            new_file.download("sticker.tgs")
            new_files = bot.get_file(file_id)
            new_files.download("sticker.tgs.rename_me")
            bot.sendDocument(chat_id, document=open("sticker.tgs.rename_me", "rb"))
            bot.sendChatAction(chat_id, "upload_animated")
            bot.sendDocument(chat_id, document=open("sticker.tgs", "rb"))
            os.remove("sticker.tgs")
            os.remove("sticker.tgs.rename_me")
        else:
            file_id = msg.reply_to_message.sticker.file_id
            new_file = bot.get_file(file_id)
            new_file.download("sticker.webm")
            bot.sendDocument(chat_id, document=open("sticker.webm", "rb"))
            bot.sendChatAction(chat_id, "upload_video")
            bot.sendVideo(chat_id, video=open("sticker.webm", "rb"))
            os.remove("sticker.webm")
        return
    else:
        update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG or TGS or WEBM for video sticker."
        )


def kang(update, context):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    is_animated = False
    is_video = False
    file_id = None
    sticker_emoji = "🤔"
    sticker_data = None

    # The kang syntax is as follows:
    # /kang 🤔 <as reply to document>
    # /kang http://whatever.com/sticker.png 🤔
    # It can be animated or not.

    # first check if we're syntactically correct.
    if not msg.reply_to_message and not args:
        # this is quite a bit more difficult, we need to get all their packs managed by us.
        packs = ""
        # start with finding non-animated packs.
        packnum = 0
        # Initial pack name for non-animated
        packname = f"stickers_{user.id}_by_{context.bot.username}"
        # Max non-animated stickers in a pack
        max_stickers = 120

        # Find the packs
        while True:
            last_set = False
            try:
                stickerset = context.bot.get_sticker_set(packname)
                if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    if not is_animated and not is_video:
                        packname = (
                            f"stickers_{packnum}_{user.id}_by_{context.bot.username}"
                        )
                    elif is_animated:
                        packname = f"stickers_animated{packnum}_{user.id}_by_{context.bot.username}"
                    else:
                        packname = f"stickers_video{packnum}_{user.id}_by_{context.bot.username}"
                else:
                    last_set = True
                packs += f"[{'animated ' if is_animated and not is_video else '' or 'video ' if is_video else ''}pack{packnum if packnum != 0 else ''}](t.me/addstickers/{packname})\n"
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    last_set = True
                else:
                    print(e)
                    break  # something went wrong, leave the loop and send what we have.

            # If we're done checking bot animated, video, and non-animated and non-video packs
            # exit the loop and send our pack message.
            if last_set and is_animated and is_video:
                break
            elif last_set and not is_animated:
                # move to checking animated packs. Start with the first pack
                packname = f"stickers_animated_{user.id}_by_{context.bot.username}"
                # reset our counter
                packnum = 0
                # Animated packs have a max of 50 stickers
                max_stickers = 50
                # tell the loop we're looking at animated stickers now
                is_animated = True
            elif last_set and not is_video:
                # move to checking video packs. Start with the first pack
                packname = f"stickers_video_{user.id}_by_{context.bot.username}"
                # reset our counter
                packnum = 0
                # Video packs have a max of 50 stickers
                max_stickers = 50
                # tell the loop we're looking at video stickers now
                is_video = True

        # if they have no packs, change our message
        if not packs:
            packs = "Looks like you don't have any packs! Please reply to a sticker, or image or video .webm format to kang it and create a new pack!"
        else:
            packs = (
                "Please reply to a sticker, or image to kang it!\nOh, by the way, here are your packs:\n"
                + packs
            )

        # Send our list as a reply
        msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)

        # Don't continue processing the command.
        return

    # User sent /kang in reply to a message
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            is_animated = msg.reply_to_message.sticker.is_animated
            is_video = msg.reply_to_message.sticker.is_video
            file_id = msg.reply_to_message.sticker.file_id
            # also grab the emoji if the user wishes
            if not args:
                sticker_emoji = msg.reply_to_message.sticker.emoji
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        elif msg.reply_to_message.video:
            file_id = msg.reply_to_message.video.file_id
        else:
            msg.reply_text("Yea, I can't steal that.")
            return

        # Check if they have an emoji specified.
        if args:
            sticker_emoji = args[0]

        # Download the data
        kang_file = context.bot.get_file(file_id)
        sticker_data = kang_file.download(out=io.BytesIO())
        # move to the front of the buffer.
        sticker_data.seek(0)
    else:  # user sent /kang with url
        url = args[0]
        # set the emoji if they specify it.
        if len(args) >= 2:
            sticker_emoji = args[1]
        # open the URL, downlaod the image and write to
        # a buffer object we can use elsewhere.
        sticker_data = io.BytesIO()
        try:
            resp = urllib.urlopen(url)

            # check the mime-type first, you can't kang a .html file.
            mime = resp.getheader("Content-Type")
            if mime not in [
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/webp",
                "application/x-tgsticker",
                "video/webm",
            ]:
                msg.reply_text("I can only kang images and video .webm format.")
                return

            # check if it's an animated sticker type
            if not mime == "video/webm" and not mime == "application/x-tgsticker":
                is_video = False
                is_animated = False
            # check if it's an animated sticker type
            elif mime == "application/x-tgsticker":
                is_animated = True
            else:
                is_video = True

            # write our sticker data to a buffer object
            sticker_data.write(resp.read())
            # move to the front of the buffer.
            sticker_data.seek(0)
        except ValueError:
            # If they gave an invalid URL
            msg.reply_text("Yea, that's not a URL I can download from.")
            return
        except HTTPError as e:
            # if we're not allowed there for some reason
            msg.reply_text(f"Error downloading the file: {e.code} {e.msg}")
            return

    packnum = 0
    packname_found = False
    invalid = False

    # now determine the pack name we should use by default
    if not is_animated and not is_video:
        packname = f"stickers_{user.id}_by_{context.bot.username}"
        max_stickers = 120
    elif is_animated:
        packname = f"stickers_animated_{user.id}_by_{context.bot.username}"
        max_stickers = 50
    else:
        packname = f"stickers_video_{user.id}_by_{context.bot.username}"
        max_stickers = 50

    # Find if the pack is full already
    while not packname_found:
        try:
            stickerset = context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                if not is_animated and not is_video:
                    packname = f"stickers_{packnum}_{user.id}_by_{context.bot.username}"
                elif is_animated:
                    packname = f"stickers_animated{packnum}_{user.id}_by_{context.bot.username}"
                else:
                    packname = (
                        f"stickers_video{packnum}_{user.id}_by_{context.bot.username}"
                    )
            else:
                packname_found = True
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = True
                # we will need to create the sticker pack
                invalid = True

    # if the image isn't animated, ensure it's the right size/format with PIL
    if not is_animated and not is_video:
        # handle non-animated stickers.
        try:
            im = Image.open(sticker_data)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if size1 > size2:
                    scale = 512 / size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512 / size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                maxsize = (512, 512)
                im.thumbnail(maxsize)
            # Saved the resized sticker in memory
            sticker_data = io.BytesIO()
            im.save(sticker_data, "PNG")
            # seek to start of the image data
            sticker_data.seek(0)
        except OSError as e:
            msg.reply_text("I can only steal images and .webm video format.")
            return

    # actually add the damn sticker to the pack, animated or not.
    try:
        # Add the sticker to the pack if it doesn't exist already
        if invalid:
            # Since Stickerset_invalid will also try to create a pack we might as
            # well just reuse that code and avoid typing it all again.
            raise TelegramError("Stickerset_invalid")
        context.bot.add_sticker_to_set(
            user_id=user.id,
            name=packname,
            png_sticker=sticker_data if not is_animated and not is_video else None,
            tgs_sticker=sticker_data if is_animated else None,
            webm_sticker=sticker_data if is_video else None,
            emojis=sticker_emoji,
        )
        msg.reply_text(
            f"Your sticker successfully added to your pack!\nEmoji is: {sticker_emoji}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "View Pack", url=f"t.me/addstickers/{packname}"
                        )
                    ]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramError as e:
        if e.message == "Stickerset_invalid":
            # if we need to make a sticker pack, make one and make this the
            # first sticker in the pack.
            makepack_internal(
                update,
                context,
                msg,
                user,
                sticker_emoji,
                packname,
                packnum,
                png_sticker=sticker_data if not is_animated and not is_video else None,
                tgs_sticker=sticker_data if is_animated else None,
                webm_sticker=sticker_data if is_video else None,
            )
        elif e.message == "Stickers_too_much":
            msg.reply_text("Max packsize reached. Press F to pay respect.")
        elif e.message == "Invalid sticker emojis":
            msg.reply_text("I can't kang with that emoji!")
        elif e.message == "Internal Server Error: sticker set not found (500)":
            msg.reply_text(
                f"Sticker successfully added to your pack!\nEmoji is: {sticker_emoji}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "View Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg.reply_text(
                f"Oops! looks like something happened that shouldn't happen! ({e.message})"
            )
            raise


def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
    webm_sticker=None,
):
    name = user.first_name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = f" {packnum}"
        success = context.bot.create_new_sticker_set(
            user.id,
            packname,
            f"{name} {'animated ' if tgs_sticker else '' or 'video ' if webm_sticker else ''}pack by [@{context.bot.username}]{extra_version}",
            tgs_sticker=tgs_sticker or None,
            png_sticker=png_sticker or None,
            webm_sticker=webm_sticker or None,
            emojis=emoji,
        )

    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            msg.reply_text(
                "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                parse_mode=ParseMode.MARKDOWN,
            )

            return
        elif e.message in ("Peer_id_invalid", "bot was blocked by the user"):
            msg.reply_text(
                "Contact me in PM first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Start",
                                url=f"t.me/{context.bot.username}",
                            )
                        ]
                    ]
                ),
            )

            return
        elif e.message == "Internal Server Error: created sticker set not found (500)":
            success = True
        else:
            success = False
    if success:
        msg.reply_text(
            f"Your stickers pack successfully created!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "View Pack", url=f"t.me/addstickers/{packname}"
                        )
                    ]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")


def delsticker(update, context):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        context.bot.delete_sticker_from_set(file_id)
        msg.reply_text("Deleted!")
    else:
        update.effective_message.reply_text(
            "Please reply to sticker message to del sticker"
        )


__help__ = """
• `/stickerid`*:* reply to a sticker to me to tell you its file ID.
• `/getsticker`*:* reply to a sticker to me to upload its raw PNG file.
• `/kang`*:* reply to a sticker to add it to your pack.
• `/stickers`*:* Find stickers for given term on combot sticker catalogue
"""

__mod_name__ = "🎉 sᴛɪᴄᴋᴇʀ"
STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, run_async=True)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, run_async=True)
KANG_HANDLER = DisableAbleCommandHandler(
    ["kang", "steal"], kang, admin_ok=True, run_async=True
)
STICKERS_HANDLER = DisableAbleCommandHandler("stickers", cb_sticker, run_async=True)
DEL_HANDLER = DisableAbleCommandHandler("delsticker", delsticker, run_async=True)

dispatcher.add_handler(STICKERS_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
dispatcher.add_handler(KANG_HANDLER)
dispatcher.add_handler(DEL_HANDLER)
