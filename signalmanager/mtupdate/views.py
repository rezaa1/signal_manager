from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from signals.models import Signal, Account
from django.db.models import Exists,OuterRef
from trades.models import Trade
from signals.serializers import SignalSerializer,AccountSerializer
from signals.models import Bot
from signals.models import Channel
from signals.models import MessageRecord
from telegram import bot
from background_task import background
from trades.apps import manage_trades
import telegram
import signals
import sys
#from config import telegram_token_news


def get_standard_symbol(symbol):

    rsymbol = symbol.split('-e')[0]

    return(rsymbol)



@api_view(['GET', 'POST'])
def mtupdate_list(request):
    """
    List all code signals, or create a new signal.
    """
    update=False
    if request.method == 'GET':
        signals = Signal.objects.filter(owner=request.user).exclude(order_status='Deleted')
        serializer = SignalSerializer(signals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            signal = Signal.objects.get(owner=request.user,order_id=request.data['order_id'])
            serializer = SignalSerializer(signal, data=request.data)
            update=True
        except Signal.DoesNotExist:
            serializer = SignalSerializer(data=request.data)

        if serializer.is_valid():
            if update:
               #send_update(request.data,signal)
               order_update=generate_update(request=request.data,data=signal)
               message=generate_message(request=request.data,data=signal)
               serializer.save(owner=request.user)
               manage_channels(signal.id,message,update)
               manage_trades(signal.id,update=order_update)
            else:
               message=generate_message(request=request.data,data=None)
               serializer.save(owner=request.user,standard_symbol=get_standard_symbol(request.data['order_symbol']))
               signal = Signal.objects.get(owner=request.user,order_id=request.data['order_id'])
               manage_channels(signal.id,message,update)
               manage_trades(signal.id)
               #id=send_update(request.data)
               #serializer.save(owner=request.user,message_id=id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Quick fix to get active list only, needs to be fixed later.
@api_view(['GET', 'POST'])
def mtupdate_list_active(request):
    """
    List all code signals, or create a new signal.
    """
    update=False
    if request.method == 'GET':
        signals = Signal.objects.filter(owner=request.user).exclude(order_status='Deleted').exclude(order_status='Closed')
        serializer = SignalSerializer(signals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            print("DBGGG view mtupdate post")
            signal = Signal.objects.get(owner=request.user,order_id=request.data['order_id'])
            serializer = SignalSerializer(signal, data=request.data)
            update=True
        except Signal.DoesNotExist:
            serializer = SignalSerializer(data=request.data)

        if serializer.is_valid():
            if update:
               #send_update(request.data,signal)
               order_update=generate_update(request=request.data,data=signal)
               message=generate_message(request=request.data,data=signal)
               serializer.save(owner=request.user)
               print("DBG before gen message",signal.__dict__)
               manage_channels(signal.id,message,update)
               manage_trades(signal.id,update=order_update)
            else:
               message=generate_message(request=request.data,data=None)
               serializer.save(owner=request.user)
               signal = Signal.objects.get(owner=request.user,order_id=request.data['order_id'])
               manage_channels(signal.id,message,update)
               manage_trades(signal.id)
               #id=send_update(request.data)
               #serializer.save(owner=request.user,message_id=id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def mtaccount_list(request):
    """
    List all code signals, or create a new signal.
    """
    update=False
    if request.method == 'GET':
        accounts = Account.objects.filter(owner=request.user)
        serializer = AccountSerializer(signals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            print("DBGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
            account = Account.objects.get(owner=request.user,login=request.data['login'])
            serializer = AccountSerializer(account, data=request.data)
            update=True
        except Account.DoesNotExist:
            serializer = AccountSerializer(data=request.data)

        if serializer.is_valid():
            if update:
               #send_update(request.data,signal)
               order_update=generate_update(request=request.data,data=account)
               serializer.save(owner=request.user)
            else:
               message=generate_message(request=request.data,data=None)
               serializer.save(owner=request.user)
               account = Account.objects.get(owner=request.user,login=request.data['login'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def mtupdate_detail(request, pk):
    """
    Retrieve, update or delete a code signal.
    """
    try:
        signal = Signal.objects.get(pk=pk)
    except Signal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignalSerializer(signal)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SignalSerializer(signal, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        signal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'PUT', 'DELETE'])
def mtaccount_detail(request, pk):
    """
    Retrieve, update or delete a code signal.
    """
    try:
        account = Account.objects.get(pk=pk)
    except account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SignalSerializer(signal, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        signal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@background(queue='channel-queue')
def manage_channels(signal_id,message,update):
    nl="\n"
    
    print("DBG_manage_channels_message1",message)
    print("DBG_manage_channels update",update)
    data= Signal.objects.get(pk=signal_id) 
    owner=data.owner
    signal_id=data.id
    print("DBG_manage_channel_owner",owner)
    # get bot
    bot = Bot.objects.get(owner=owner)
    # get list of channels for user
    channels = Channel.objects.filter(owner=owner)

    # find signal refrence in message id channel id  for each cannel
    # send signal update for each channel
    # save status
    mid=0
    for channel in channels:
        print("DBG__channel",channel)
        if update:
            try:
                messagerecord = MessageRecord.objects.get(channel=channel,signal=data,owner=owner) 
                mid=messagerecord.message_id
                midfound=True
                print("DBG_manage_channel_update_mid10",mid)
                mid, new =send_message(channel=channel.channel_id,token=bot.token,message=message,message_id=mid)   
                if new:
                    messagerecord.message_id= mid
                    messagerecord.save()
                print("DBG_manage_channel_update_mid11",mid)
            except ObjectDoesNotExist:
                print("DBG_manage_channel_update_exception20")
                message="DELAYED "+generate_message(data.__dict__)+nl+message
                mid=0
                midfound=False
                print("DBG_manage_channel_update_exception21")
                mid, new =send_message(channel=channel.channel_id,token=bot.token,message=message)   
                print("DBG_manage_channel_update_exception22")
            except:
                print("Unexpected error:", sys.exc_info()[0])
        else:
            try: 
                print("DBG_manage_trying to get mid")
                messagerecord = MessageRecord.objects.get(channel=channel,signal=data,owner=owner) 
                mid=messagerecord.message_id
                print("DBG_manage_trying to get mid is ",mid)
                message="Repeating message as New:"+nl+message
                midfound=True
                print("DBG_manage_trying to send message ",message)
                mid, new =send_message(channel=channel.channel_id,token=bot.token,message=message,message_id=mid)   
                print("DBG_manage_sent message mid is",mid)
            except ObjectDoesNotExist:
                print("DBG_manage_new_",message)
                mid, new =send_message(channel=channel.channel_id,token=bot.token,message=message)
                midfound=False
            except:
                print("Unexpected error:", sys.exc_info()[0])

        print("DBG_manage_channel_message",message)
        if mid != 0 and midfound==False:
            print("DBG_updating mid")
            #print("MessageRecord(channel_id=",channel.channel_id,",signal_id=",signal_id,",message_id=",mid,") ")
            #messagerecord = MessageRecord(channel_id=channel.channel_id,signal_id=signal_id,message_id=mid) 
            messagerecord = MessageRecord(owner=owner,channel=channel,signal=data,message_id=mid) 
            messagerecord.save()
        
def generate_message(request,data=None):
    print("DBG_generate_message_request",request)
    if data != None: print("DBG_generate_message_data",data.__dict__)
    nl="\n"
    ORDER_TYPE = ["BUY" , "SELL" ,"Pending Order BUY LIMIT" , "Pending Order SELL LIMIT" , "Pending Order BUY STOP", "Pending Order  SELL STOP" ]

    if data == None:
        message="SIGNAL:"+nl
        message=message+ ORDER_TYPE[int(request['order_type'])] + " "+request['order_symbol'] + nl+ " AT: "  + request['order_price']  
        if 'order_stoploss' in request:
            message=message+ nl + " SL: " + request['order_stoploss'] 
        if 'order_takeprofit' in request:
            message=message+ nl + " TP: " + request['order_takeprofit']
    else:
        message="updating "
        if 'order_stoploss' in request:
            if data.order_stoploss != request['order_stoploss']:
                message= message + "Move SL to: "+request['order_stoploss'] +nl
        if 'order_takeprofit' in request:
            if data.order_takeprofit != request['order_takeprofit']:
                message= message + "Move TP to: "+request['order_takeprofit'] + nl
        if data.order_price != request['order_price']:
            message= message + "Move order price to: "+request['order_price'] + nl
        if data.order_status != request['order_status']:
            message= message + "status changed : " + request['order_status'] + nl
        if data.order_type != request['order_type']:
            message= message + "type changed : " + request['order_type'] +nl
        if data.order_lot != request['order_lot']:
            message= message + "size changed : " + request['order_lot']
    print("DBGMESSAGE",message)
    return(message)

def generate_update(request,data):
    res={}
    print("DBG_generate_update_request",request)
    if data == None: 
        print("DBG_generate_message_data",data.__dict__)
        print("ERROR DATA should not be None in gen update")
    else:
        if 'order_stoploss' in request:
            if data.order_stoploss != request['order_stoploss']:
                res.update(stoploss=request['order_stoploss'])
        if 'order_takeprofit' in request:
            if data.order_takeprofit != request['order_takeprofit']:
                res.update(takeproffit=request['order_takeprofit'] )
        
        if data.order_price != request['order_price']:
            res.update(price=request['order_price'])
        if data.order_status != request['order_status']:
            res.update(status=request['order_status'] )
        if data.order_type != request['order_type']:
            res.update(type=request['order_type'] )
        if data.order_lot != request['order_lot']:
            res.update(lot=request['order_lot'])
    return(res)

def send_message(channel,token,message,message_id=0):
    print("sendmessage,channel:",channel,"token",token,"message",message,"message_id=",message_id)

    new=False
    bot = telegram.Bot(token=token)
def send_message(channel,token,message,message_id=0):
    print("sendmessage,channel:",channel,"token",token,"message",message,"message_id=",message_id)

    new=False
    bot = telegram.Bot(token=token)
    if message_id == 0:
        status = bot.send_message(chat_id=channel, text=message)
        message_id=status.message_id
        new = True
    else:
        try:
            status = bot.send_message(chat_id=channel, text=message,reply_to_message_id=message_id)
            new = False
        except:
            message = "Original MID " + message_id  + " not found \n " + messgae 
            status = bot.send_message(chat_id=channel, text=message)
            new = True
            message_id=status.message_id
             
    return(message_id, new)

