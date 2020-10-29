from django.apps import AppConfig


class MtupdateConfig(AppConfig):
    name = 'mtupdate'


def get_standard_symbol(symbol):
	rsymbol = symbol.split('-e')[0]

	return(rsymbol)


