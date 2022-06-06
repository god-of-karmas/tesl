import random
from Gopi import telethn as tbot
from telethon import events

@tbot.on(events.NewMessage(pattern="/wish"))
async def wish(alexa):
   if alexa.is_reply:
         mm = random.randint(1,100)
         lol = await alexa.get_reply_message()
         await tbot.send_message(alexa.chat_id, f"**Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=lol)
   if not alexa.is_reply:
         mm = random.randint(1,100)
         ALEXA = "https://telegra.ph/file/6760471209d90bcad8b1f.jpg"
         await tbot.send_file(alexa.chat_id, ALEXA,caption=f"**Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=alexa)
         lol = await alexa.get_reply_message()
         await tbot.send_file(alexa.chat_id, f"**Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=lol, file=ALEXA)
   if not alexa.is_reply:
         mm = random.randint(1,100)
         ALEXA = "https://telegra.ph/file/6760471209d90bcad8b1f.jpg"
         await tbot.send_file(alexa.chat_id,f"**Your wish has been cast.✨**\n\n__chance of success {mm}%__", reply_to=lol, file=ALEXA)
         await tbot.send_file(alexa.chat_id, ALEXA,caption=f"**Your wish has been cast.✨**\n__chance of success {mm}%__", reply_to=alexa)
         lol = await alexa.get_reply_message()
         await tbot.send_file(alexa.chat_id, f"**Your wish has been cast.✨**\n__chance of success {mm}%__", reply_to=lol)
   if not alexa.is_reply:
         mm = random.randint(1,100)
         ALEXA = "https://telegra.ph/file/6760471209d90bcad8b1f.jpg"
         await tbot.send_file(alexa.chat_id, ALEXA,caption=f"**Your wish has been cast.✨**\n__chance of success {mm}%__", reply_to=lol,file=alexa)

        

