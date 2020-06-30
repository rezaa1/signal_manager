from __future__ import unicode_literals

from django.apps import AppConfig

class BotConfig(AppConfig):
    name = 'bot'

class DynaBot(DjangoTelegramBot):
    def ready(self):
        if DjangoTelegramBot.ready_run:
            return
        DjangoTelegramBot.ready_run = True

        self.mode = WEBHOOK_MODE

        bots_list = Bot.objects.all()

        if self.mode == WEBHOOK_MODE:
            webhook_site = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_SITE', None)
            if not webhook_site:
                logger.warn('Required TELEGRAM_WEBHOOK_SITE missing in settings')
                return
            if webhook_site.endswith("/"):
                webhook_site = webhook_site[:-1]

            webhook_base = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_PREFIX','/')
            if webhook_base.startswith("/"):
                webhook_base = webhook_base[1:]
            if webhook_base.endswith("/"):
                webhook_base = webhook_base[:-1]

            cert = settings.DJANGO_TELEGRAMBOT.get('WEBHOOK_CERTIFICATE', None)
            certificate = None
            if cert and os.path.exists(cert):
                logger.info('WEBHOOK_CERTIFICATE found in {}'.format(cert))
            #    certificate=open(cert, 'rb')
                certificate=cert
            elif cert:
                logger.error('WEBHOOK_CERTIFICATE not found in {} '.format(cert))

        for b in bots_list:
            print(b)
            token = b.get('TOKEN', None)
            if not token:
                break

            allowed_updates = b.get('ALLOWED_UPDATES', None)
            timeout = b.get('TIMEOUT', None)

            if self.mode == WEBHOOK_MODE:
                try:
                    bot = telegram.Bot(token=token)
                    DjangoTelegramBot.dispatchers.append(Dispatcher(bot, None, workers=0))
                    hookurl = '{}/{}/{}/'.format(webhook_site, webhook_base, token)

                    max_connections = b.get('WEBHOOK_MAX_CONNECTIONS', 40)

                    setted = bot.setWebhook(hookurl, certificate=certificate, timeout=timeout, max_connections=max_connections, allowed_updates=allowed_updates)
                    webhook_info = bot.getWebhookInfo()
                    real_allowed = webhook_info.allowed_updates if webhook_info.allowed_updates else ["ALL"]

                    bot.more_info = webhook_info
                    logger.warning('Telegram Bot <{}> setting webhook [ {} ] max connections:{} allowed updates:{} pending updates:{} : {}'.format(bot.username, webhook_info.url, webhook_info.max_connections, real_allowed, webhook_info.pending_update_count, setted))
                    print("botok")
                except InvalidToken:
                    logger.error('Invalid Token : {}'.format(token))
                    return
                except TelegramError as er:
                    logger.error('Error : {}'.format(repr(er)))
                    return

            else:
                try:
                    updater = Updater(token=token)
                    bot = updater.bot
                    bot.delete_webhook()
                    DjangoTelegramBot.updaters.append(updater)
                    DjangoTelegramBot.dispatchers.append(updater.dispatcher)
                    DjangoTelegramBot.__used_tokens.add(token)
                except InvalidToken:
                    logger.error('Invalid Token : {}'.format(token))
                    return
                except TelegramError as er:
                    logger.error('Error : {}'.format(repr(er)))
                    return

            DjangoTelegramBot.bots.append(bot)
            DjangoTelegramBot.bot_tokens.append(token)
            DjangoTelegramBot.bot_usernames.append(bot.username)


        logger.debug('Telegram Bot <{}> set as default bot'.format(DjangoTelegramBot.bots[0].username))

def start_bots():

	bots = DynaBot()
	bots.ready()
	