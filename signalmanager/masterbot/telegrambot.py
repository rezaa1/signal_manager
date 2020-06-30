# -*- coding: utf-8 -*-
# Example code for telegrambot.py module
from django_telegrambot.apps import DjangoTelegramBot
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from django.contrib.auth.models import User
from signals.models import Bot 
from signals.models import Channel
import telegram



import logging
logger = logging.getLogger(__name__)

import logging.config
LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
    # root logger
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
})

CHOOSING, TYPING_REPLY, TYPING_CHOICE , CHANNEL_CHOICE , CHANNEL_REPLY , BOT_CHOICE, BOT_REPLY = range(7)

#def forwarded(bot, update):
#    bot.sendMessage(update.message.chat_id, text='This msg forwaded information:\n {}'.format(update.effective_message))
#

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


#def echo(bot, update):
#    update.message.reply_text(update.message.text)
#

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


reply_keyboard = [['Register your bot', 'Register a new channel' ],
                  ['Trading Platform'],
                  ['Done']]
reply_keyboard_init = [['Signall Provider' ],['Signall copier']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_init = ReplyKeyboardMarkup(reply_keyboard_init, one_time_keyboard=True)
global userinfo
class UserInfo:
    def get_bot(self):
        try:
            self.bot = Bot.objects.get(owner_id = self.user_id)
        except:
            raise
            pass

    def get_channel(self):
        try:
            channels = Channel.objects.filter(owner_id = self.user_id)
            if len(channels) > 0:
               self.channels = channels 
        except:
            pass

    def __init__(self,update):
        self.username=update.message.chat.username
        self.name=update.message.chat.first_name
        self.telegram_id=update.message.chat.id
        self.bot = None
        self.channels = None
        try:
            print("DBG Looking for:",self.username,self.name,self.telegram_id)
            user = User.objects.select_related('profile').select_related('auth_token').get(profile__telegram_id=self.telegram_id)
            self.newuser=False
            self.user_id= user.id
            self.get_bot()
            self.apikey=user.auth_token
            self.get_channel()
        except:
            raise
            user = User.objects.create_user(first_name=self.name, last_name='',username=self.username)
            user.profile.signal_provider=True
            user.profile.telegram_id=self.telegram_id
            user.save
            user.profile.save()
            self.newuser=True
            self.user_id= user.id

    def update_bot(self,bot_id, first_name,username):
        try:
            botdb = Bot.objects.get(owner_id = self.user_id, bot_id = bot_id)
            botdb.bot_id=bot_id
            botdb.first_name = first_name
            botdb.username = username
        except:
            botdb = Bot(bot_id=bot_id,title=title,owner_id= self.user_id)
        botdb.save()
        self.get_bot()

    def update_channel(self,channel_id,title):
        try:
            channel = Channel.objects.get(owner_id = self.user_id, channel_id = channel_id )
            channel.channel_id=channel_id
            channel.title = title
        except:
            channel= Channel(channel_id=channel_id,title=title,owner_id= self.user_id)
        
        channel.save()
        self.get_channel()


def start(bot,update):
    global userinfo 
    userinfo = UserInfo(update)

    if userinfo.newuser:
        msg="Hi "+userinfo.name+","
    else:
        msg="Welcome back "+userinfo.name+","
    bot.sendMessage(update.message.chat_id,text=
        msg +
        ("My name is Trade Manager.\n"
         " I will help you in managing signalls and send updates to your subscribers.\n"
        " You need to register a bot and add your channel here then install the metatrader EA.\n" 
        "Please choose from these options"),
        reply_markup=markup)

    return CHOOSING


def register_bot_choice(bot,update):
    logger.warning("register_bot_choice")
    bot.sendMessage(update.message.chat_id,text=
        'Alright, please go to @BotFather and register a new bot, then send me your bot token:') 

    return BOT_REPLY

def trading_platform_choice(bot,update):
    global userinfo
    logger.warning("trading_platform_choice")
    bot.sendMessage(update.message.chat_id,text=
        'Alright, note your token: [{}]'.format(userinfo.apikey)) 
    return CHANNEL_REPLY

def register_channel_choice(bot,update):
    logger.warning("register_channel_choice")
    bot.sendMessage(update.message.chat_id,text=
        'Alright, please forward me a message from your channel first, ') 
    return CHANNEL_REPLY

def bot_information(bot,update):
    logger.warning("bot_information")

    print(userinfo)
    newtoken = update.message.text
    tid=update.message.chat.id

    newbot = telegram.Bot(token=newtoken)
    try:
        bot_info=newbot.getMe()
#       {'id': 752542063, 'first_name': 'testbot', 'is_bot': True, 'username': 'p1234567890bot'}
        if bot_info['is_bot'] == True:
                userinfo.update_bot(bot_id=bot_info.id, first_name=bot_info['first_name'],username=bot_info['username'])
                bot.sendMessage(update.message.chat_id, text="Neat!"
                           "name: {} , username{}".format(userinfo.bot.first_name,userinfo.bot.username), reply_markup=markup) 
        else:
                bot.sendMessage(update.message.chat_id, text="Owch! this is not correct info for bot, try again")
                return BOT_REPLY
        return CHOOSING


    #except (telegram.error.Unauthorized,telegram.error.InvalidToken) as e:
    except:
        bot.sendMessage(update.message.chat_id, text="owch! invalid tokenn, try again", reply_markup=markup) 
        return BOT_REPLY

def channel_information(bot,update):
    global userinfo 
    logger.warning("channel_information")
    cid = update.message.forward_from_chat.id
    title = update.message.forward_from_chat.title
    userbot=  telegram.Bot(token=userinfo.bot.token)
    print("DBG getting chatinfo",cid,userinfo.bot.bot_id) 
    try:
        chatinfo=userbot.getChatMember(chat_id=cid,user_id=userinfo.bot.bot_id)
    except: 
        bot.sendMessage(update.message.chat_id, text="Bot [{}]  is not member of Channel  [{}] , please make sure you added this bot as an administrator with post message permission and try again".format(userinfo.bot.username,title), reply_markup=markup)
        return CHOOSING

        #{'user': {'id': 709168516, 'first_name': 'providerbot', 'is_bot': True, 'username': 'provider123bot'}, 'status': 'administrator', 'can_be_edited': False, 'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True, 'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True, 'can_promote_members': False, 'until_date': None}
    print("DBG chatinfo",chatinfo) 
    print("DBG chatinfo",chatinfo.can_post_messages) 
    if chatinfo.status  == 'administrator' and chatinfo.can_post_messages:
        print("DBG chatio p1") 
        userinfo.update_channel(cid,title)
        print("DBG chatio p2") 
        bot.sendMessage(update.message.chat_id, text="Neat! channel added"
                              "id: {}, title {}".format(cid,title), reply_markup=markup) 
    else:
        bot.sendMessage(update.message.chat_id, text="Bot [{}]  doesn't have enough permissions for Channel  [{}] , please make sure you added this bot as an administrator with post message permission and try again".format(userinfo.bot.username,title), reply_markup=markup)
    return CHOOSING



def received_information(bot, update):
    print("received_information",update)
    print("---------------------------------")
    print("received_information_context",context)
    text = update.message.text

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{}"
                              "You can tell me more, or change your opinion on something.".format(
                                  "ss"), reply_markup=markup)

    return CHOOSING


def done(update, context):


    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    dps=[]
    num_bots=len(DjangoTelegramBot.bots)
    #dp=[None] * num_bots

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY

    for token in DjangoTelegramBot.bot_tokens:
       logger.info("Loading handlers for telegram bot {} ".format(token))
       dps.append( DjangoTelegramBot.getDispatcher(bot_id=token))     #get by bot token

    # on different commands - answer in Telegram
    for i  in range(0,len(dps)):
       dps[i].add_handler(conv_handler)
       dps[i].add_error_handler(error)


#+++++++++++++++++


conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [
                       RegexHandler('^Register your bot$', register_bot_choice),
                       RegexHandler('^Register a new channel$', register_channel_choice),
                       RegexHandler('^Trading Platform$', trading_platform_choice),
                      ],
            CHANNEL_REPLY: [MessageHandler(Filters.text, channel_information), ],
            BOT_REPLY: [MessageHandler(Filters.text, bot_information), ],
        },

        fallbacks=[RegexHandler('^Done$', done)]
)



if __name__ == '__main__':
    main()
