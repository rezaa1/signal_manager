from django.apps import AppConfig


class MtupdateConfig(AppConfig):
    name = 'mtupdate'


def manage_trades(symbol):
	rsymbol = symbol.split('-e')[0]

	return(rsymbol)


