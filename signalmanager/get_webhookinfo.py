import importlib
import telegram
tokens=['752542063:AAGlNKZYzC66hYg_OKszR0s9LV2BN_CAGYs', '707460578:AAHeaMERI31R7OUPn-6gds6n2toERPS6z8Q' ]
while True:
 print("=======================================================================")
 for token in tokens:
  bot = telegram.Bot(token=token)
  webhook_info = bot.getWebhookInfo()
  real_allowed = webhook_info.allowed_updates if webhook_info.allowed_updates else ["ALL"]
  bot.more_info = webhook_info
  print('Bot {}  max connections:{} allowed updates:{} pending updates:{} , Errordate:{} '.format(bot.username, webhook_info.max_connections, real_allowed, webhook_info.pending_update_count,  webhook_info.last_error_date))
  print(webhook_info) 

