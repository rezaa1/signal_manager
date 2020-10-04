from telegram import bot

import telegram


def send_update(msg):

   bot = telegram.Bot(token="707460578:AAFb-HVEgz6LFJqHyZVPPOLbF8D7lWh_8wI")
   status = bot.send_message(chat_id="-1001415922072", text="updates" )
   print(status)
   status = bot.send_message(chat_id="-1001415922072", text="updates2" , reply_to_message_id=status.message_id)

   print(status)

send_update("test")
