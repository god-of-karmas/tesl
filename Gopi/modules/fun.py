import html
import random
import time

from telegram import ParseMode, Update, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import escape_markdown

import Gopi.modules.fun_strings as fun
from Gopi import DEMONS, DRAGONS, dispatcher
from Gopi.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from Gopi.modules.helper_funcs.alternate import typing_action
from Gopi.modules.helper_funcs.chat_status import (is_user_admin)
from Gopi.modules.helper_funcs.extraction import extract_user

GN_IMG= "https://te.legra.ph/file/314c36cf0fa2c4006e9fe.jpg"
DECIDE_IMG= "https://te.legra.ph/file/d5e4e6a1b6414b0d4444d.mp4"
JUDGE_IMG= "https://te.legra.ph/file/d85924f1325458ed6d99e.jpg"


@typing_action
def goodnight(update, context):
    message = update.effective_message
    first_name = update.effective_user.first_name
    reply = f"*Hey {escape_markdown(first_name)} \nGood Night! 😴*"
    message.reply_photo(GN_IMG,reply, parse_mode=ParseMode.MARKDOWN)

GM_IMG= "https://te.legra.ph/file/314c36cf0fa2c4006e9fe.jpg"
@typing_action
def goodmorning(update, context):
    message = update.effective_message
    first_name = update.effective_user.first_name
    reply = f"*Hey {escape_markdown(first_name)} \n Good Morning!☀*"
    message.reply_photo(GM_IMG,reply, parse_mode=ParseMode.MARKDOWN)

    
def gbun(update, context):
    user = update.effective_user
    chat = update.effective_chat

    if update.effective_message.chat.type == "private":
        return
    if int(user.id) in DRAGONS or int(user.id) in DEMONS:
        context.bot.sendMessage(chat.id, (random.choice(fun.GBUN)))


def gbam(update, context):
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    message = update.effective_message

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id:
        gbam_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(gbam_user.first_name)

    else:
        user1 = curr_user
        user2 = bot.first_name

    if update.effective_message.chat.type == "private":
        return
    if int(user.id) in DRAGONS or int(user.id) in DEMONS:
        gbamm = fun.GBAM
        reason = random.choice(fun.GBAM_REASON)
        gbam = gbamm.format(user1=user1, user2=user2, chatid=chat.id, reason=reason)
        context.bot.sendMessage(chat.id, gbam, parse_mode=ParseMode.HTML)


def judge(update, context):
    context.bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(fun.JUDGE_HANDLER))
    else:
      message.reply_text(fun.JUDGE_STRINGS)
      
      
def alexa(update, context):
    context.bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(fun.ALEXA_HANDLER))
    else:
      message.reply_text(fun.ALEXA_STRINGS)


def decide(update, context):
    context.bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(fun.DECIDE_HANDLER))
    else:
      message.reply_text(fun.DECIDE_STRINGS)


@typing_action
def repo(update, context):
    update.effective_message.reply_text(fun.REPO)
  

def insult(update, context):
    context.bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(fun.SFW_STRINGS))
    else:
      message.reply_text(random.choice(fun.SFW_STRINGS)) 
    
    
def abuse(update, context):
    context.bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(fun.ABUSE_STRINGS))
    else:
      message.reply_text(random.choice(fun.ABUSE_STRINGS))


def slap(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    reply_text = message.reply_to_message.reply_text if message.reply_to_message else message.reply_text

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id == bot.id:
        temp = random.choice(fun.SLAP_ALEXA_TEMPLATES)

        if isinstance(temp, list):
            if temp[2] == "tmute":
                if is_user_admin(chat, message.from_user.id):
                    reply_text(temp[1])
                    return

                mutetime = int(time.time() + 60)
                bot.restrict_chat_member(
                    chat.id,
                    message.from_user.id,
                    until_date=mutetime,
                    permissions=ChatPermissions(can_send_messages=False))
            reply_text(temp[0])
        else:
            reply_text(temp)
        return

    if user_id:

        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    temp = random.choice(fun.SLAP_TEMPLATES)
    item = random.choice(fun.ITEMS)
    hit = random.choice(fun.HIT)
    throw = random.choice(fun.THROW)

    if update.effective_user.id == 1342820594:
        temp = "@AsadSupport scratches {user2}"

    reply = temp.format(
        user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(reply, parse_mode=ParseMode.HTML)   
    

@typing_action
def truth(update, context):
    update.effective_message.reply_text(random.choice(fun.TRUTH))


@typing_action
def dare(update, context):
    update.effective_message.reply_text(random.choice(fun.DARE))
 

def pat(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    message = update.effective_message

    reply_to = message.reply_to_message if message.reply_to_message else message

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id:
        patted_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(patted_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    pat_type = random.choice(("Text", "Gif", "Sticker"))
    if pat_type == "Gif":
        try:
            temp = random.choice(fun.PAT_GIFS)
            reply_to.reply_animation(temp)
        except BadRequest:
            pat_type = "Text"

    if pat_type == "Sticker":
        try:
            temp = random.choice(fun.PAT_STICKERS)
            reply_to.reply_sticker(temp)
        except BadRequest:
            pat_type = "Text"

    if pat_type == "Text":
        temp = random.choice(fun.PAT_TEMPLATES)
        reply = temp.format(user1=user1, user2=user2)
        reply_to.reply_text(reply, parse_mode=ParseMode.HTML)
       
    
GOODMORNING_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodmorning|good morning)"), goodmorning, friendly="goodmorning", run_async=True)
GOODNIGHT_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodnight|good night)"), goodnight, friendly="goodnight", run_async=True)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)

REPO_HANDLER = DisableAbleCommandHandler("repo", repo, run_async=True)

GBUN_HANDLER = CommandHandler("gbun", gbun, run_async=True)
PAT_HANDLER = DisableAbleCommandHandler("pat", pat, run_async=True)
GBAM_HANDLER = CommandHandler("gbam", gbam, run_async=True)
DARE_HANDLER = DisableAbleCommandHandler("dare", dare, run_async=True)
TRUTH_HANDLER = DisableAbleCommandHandler("truth", truth, run_async=True)
INSULT_HANDLER = DisableAbleCommandHandler("insult", insult, run_async=True)
ABUSE_HANDLER = DisableAbleCommandHandler("abuse", abuse, run_async=True)
JUDGE_HANDLER = DisableAbleCommandHandler("judge", judge, run_async=True)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide, run_async=True)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, run_async=True)
ALEXA_HANDLER = DisableAbleCommandHandler("alexa", alexa, run_async=True)

dispatcher.add_handler(GOODMORNING_HANDLER)
dispatcher.add_handler(GOODNIGHT_HANDLER)
dispatcher.add_handler(INSULT_HANDLER)
dispatcher.add_handler(ABUSE_HANDLER)
dispatcher.add_handler(GBAM_HANDLER)
dispatcher.add_handler(GBUN_HANDLER)
dispatcher.add_handler(PAT_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(JUDGE_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(ALEXA_HANDLER)

dispatcher.add_handler(TRUTH_HANDLER)
dispatcher.add_handler(REPO_HANDLER)
dispatcher.add_handler(DARE_HANDLER)
