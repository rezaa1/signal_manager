from django.apps import AppConfig


class MtupdateConfig(AppConfig):
    name = 'mtupdate'


<<<<<<< HEAD
def get_standard_symbol(symbol):
=======
def manage_trades(symbol):
>>>>>>> 7062faf0cd29a3a2820217b3eb541fe0d600852d
	rsymbol = symbol.split('-e')[0]

	return(rsymbol)


