from django.confs.urls.defaults import *
#from apps import startup

#one time startup
#startup()

from django.contrib import admin

admin.site.register(oanda.models)
