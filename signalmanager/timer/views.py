from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from signals.models import Signal
import sys
#from config import telegram_token_news

import datetime

@api_view(['GET'])
def timenow(request):
    """
    get time now in gmt 
    """
    if request.method == 'GET':
        x = datetime.datetime.utcnow()

        timestr=x.strftime("%Y%m%d %H:%M:%S")

        return Response(dict(utctime=timestr))


