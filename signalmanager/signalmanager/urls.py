from django.conf.urls import include, url
from django.urls import path
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

from trades.apps import maintain_trades
from trades.apps import maintain_price_update

from masterbot.apps import start_bots


from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views


# startup process
from django.apps import AppConfig




#from django.conf.urls import patterns
from django.contrib import admin

# Register your models here.
admin.autodiscover()

admin.site.site_header = "TradeManager Admin"
admin.site.site_title = "TradeManager Admin Portal"
admin.site.index_title = "Welcome to TradeManager Portal"


import sys
startup=True
if len(sys.argv) > 1:
   if sys.argv[1] == "makemigrations" or sys.argv[1] == "migrate":
      startup=False

if startup:
   print("STARTUP OK")
#   maintain_trades(repeat=600)
#   maintain_price_update()
#   start_bots()


API_TITLE = 'Pastebin API'
API_DESCRIPTION = 'A Web API for creating and viewing highlighted code signals.'
schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    url(r'^', include('mtupdate.urls')),
    url(r'^', include('timer.urls')),
    url(r'^', include('trades.urls')),
    url(r'^', include('signals.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^schema/$', schema_view),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('masterbot.urls')),
    url(r'^', include('django_telegrambot.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    url(r'^docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION))

]

