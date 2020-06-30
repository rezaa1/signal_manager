from telethon import TelegramClient, events

api_id = 198093
api_hash = 'b09413bcaefe07a147334e8855acdb27'

savedir="/root/tel/save/"

phone = '+61424908366'
username = 'mreza_tid'



#################3
global RISK
global live_RISK
global SaveDir
global BackupDir
global OrderFile
global OrderFileName
global backupfile
global backupfile1
global Instruments
global Instrumentspip
global  OrdersModified
global DEBUG
DEBUG=False
OrdersModified=1
global  access_token , access_token_live
access_token="6207e967d6ee40aad284e1f856139755-1462bb1f9d5c4e516c2a2e07c3e0e1d5" #trmm
access_token_democrm="acaefcca8990c76073dc4b26f5f11611-4342fe27c596e9b850cf90a57e19095b" # bomm
access_token_demobom="1d54aeace401b0f49328fe84b5d39d51-b13ebfdb3b00f30cda0550de10bf03ac" # crmm
access_token_live="664669077a8d4ce342d4e0f7e9917d72-c0303c5cbb6a57ba12db93df848773e5" # trmm


SaveDir="/root/tel/save/"
BackupDir="/root/tel/backup/"
RISK=10
live_RISK=1
backupfile=None
backupfile1=""

OrderFileName="orders.dump"
OrderFile=SaveDir+OrderFileName

import pandas

import pytz
from tzlocal import get_localzone # $ pip install tzlocal
import inspect
import datetime
from itertools import chain
import hashlib
import json
from pathlib import Path
import json
import os
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from oandapyV20.contrib.requests import ClientExtensions
from oandapyV20.contrib.requests import LimitOrderRequest
from oandapyV20.contrib.requests import StopOrderRequest
from oandapyV20.contrib.requests import TakeProfitOrderRequest

import oandapyV20.endpoints.orders as orders
import oandapyV20
from prettytable import PrettyTable
import sys, os
import termios, fcntl
from select import select
from shutil import copyfile
import csv

from postgres import Postgres

db = Postgres("postgres://signalp:password@127.0.0.1/teltrader")

global Symbols
global Oanda
Symbols=[]
Oanda=[]


global INTERACTIVE
INTERACTIVE=os.getenv('INTERACTIVE', 1 )

with open('/root/tel/save/instruments', 'r') as myfile: Instruments=myfile.read().replace('\n', ' ')
Instruments=Instruments.lower()
Instruments=Instruments.split(' ')

Instrumentspip=[]
csvReader = csv.reader(open('/root/tel/save/instruments-pip', 'rt'), delimiter=',');
for row in csvReader:
    Instrumentspip.append({"symbol":row[0] , "pip": row[1]});

###############3#


def pars_message(messages,cid,channel=None,test=False):
    global oc
    global OrdersModified
    rgx_price='((|\d)+\.\d+|\d+)'
    print("DBG in pars_message, cid:",cid)
    #ci=getChannelAID(cid)
    #print("DBG in pars_message, ci:",ci)

    #ftype=channels[ci].pars_func
    # pattern=channels[ci].signalpattern
    # fwd_from=channels[ci].fwd_from
    #if 1 == 1:
    print("DBG in pars_message, ftype:",ftype)
    try:
        #print("-----------------",messages.id,"--------------------------------------")
        msg=messages.message
        #print(messages)
        #print("-------------------------------------------------------")
        if re.match('.*(Signal Number|sell|buy).*',messages.message,re.IGNORECASE) is not None:
            msgok=1 
    except:
        print("message pars error for msg:",messages.id)
        return

    signal=0
    reorder=-1
    if messages.reply_to_msg_id != None:
        if channel == None:
            channel=client.get_entity(PeerChannel(channels[ci].id-channels[ci].copy))
        origid=get_original_msgid(messages.reply_to_msg_id,channel)
        print("-------------------------------------------------------")
        print(messages.message)
        print("looking for",messages.reply_to_msg_id,origid)
        action=""
        for t in range(0,len(MyOrders)):
            #print("MyOrders",t,MyOrders[t].msgid,"is",origid,"?",MyOrders[t].msgid-origid)
            if int(MyOrders[t].msgid) == int(origid):
                print("REPLY:",messages.message)
                print("ORDER",t,"- ",MyOrders[t].symbol)
                msg=messages.message
                msg=msg.lower()
                MyOrders[t].comment=MyOrders[t].comment+"::"+msg
                #print("REPLY2:",messages.message)
            
                msg=msg.lower()
                msg=msg.strip()
                msg=msg.replace('sl at','sl')
                msg=msg.replace('tp at','tp')
                msg=msg.replace('stoploss','sl')
                msg=msg.replace('takeprofit','tp')
                msg=msg.replace('stop loss','sl')
                msg=msg.replace('take profit','tp')
                msg=msg.replace('tp for all','tp')
                msg=msg.replace('sl for all','sl')
                msg=msg.replace('closed','close')
                msg=msg.replace('deleted','close')
                msg=msg.replace('delete\b','close ')
                msg=msg.replace('\\',' ')
                msg=msg.replace('  ',' ')
                msg=re.sub(r'[^\x00-\x7F]+',' ',msg)
                msg=msg.replace('  ',' ')
                msg=os.linesep.join([s for s in msg.splitlines() if s.strip()])

                x=msg.split(' ')
                print(x)
                c=0
                at=0
                tp=0
                sl=0
                for p in range(c,len(x)):
                    try:
                        if 'now' == x[p] and x[p+1] == "at":
                            for y in range(p+2,len(x)):
                                if re.match(rgx_price,x[y]) == x[y]:
                                    at=x[y]
                    except:
                        pass
                    if 'tp' == x[p]:
                        for y in range(p+1,len(x)):
                            if re.match(rgx_price,x[y]) == x[y]:
                                tp=x[y]
                    if 'sl' == x[p]:
                        for y in range(p+1,len(x)):
                            if sl==0 and re.match(rgx_price,x[y]) == x[y]:
                                sl=x[y]
                                c=y
                if tp != 0:
                    MyOrders[t].takeprofit=tp
                    if MyOrders[t].status < 3:
                        updateTrade(t)
                if sl != 0:
                    MyOrders[t].stoploss=sl
                    if MyOrders[t].status in [0,1,2]:
                        updateTrade(t)
                if at != 0 and MyOrders[t].status in [0,2]:
                    Notif("Action replace order",describeOrder(t))
                    cancelOrder(t)
                    MyOrders[t].atprice=at
                    MyOrders[t].status=0
                    MyOrders[t].tid=0
    
                if re.search('breakeven',msg,flags=re.IGNORECASE) != None and MyOrders[t].BE==0 and int(MyOrders[t].status) in  [2,0,1]:
                    Notif("Action brkeven",describeOrder(t))
                    breakevenTrade(t)

                if re.search('close half',msg,flags=re.IGNORECASE) != None and 'CH' not in MyOrders[t].flags and int(MyOrders[t].status) in  [2,0,1]:
                    Notif("Action Close half",describeOrder(t))
                    closeTrade(t,1,"CH")
                elif re.search('close .*hold',msg,flags=re.IGNORECASE) != None and 'CH' not in MyOrders[t].flags and int(MyOrders[t].status) in  [2,0,1]:
                    Notif("Action Close half",describeOrder(t))
                    closeTrade(t,1,"CH")
                elif re.search('don\'t close ',msg,flags=re.IGNORECASE) != None:
                    Notif("dont close detected ")
                elif re.search(r'close\b',msg,flags=re.IGNORECASE) != None and int(MyOrders[t].status) in  [2,0,1]:
                    Notif("Action Close",describeOrder(t))
                    closeTrade(t)
                        
                        
                #if re.search('sl ',msg,flags=re.IGNORECASE) != None:
                #   sl= re.sub(r'.*sl [ a-z]*(\d+.\d+).*',r'\1',msg,flags=re.DOTALL|re.IGNORECASE)
                #   MyOrders[t].sl=sl
                #   if MyOrders[t].status < 3:
                #       updateTrade(t)
                
                

                
                #print("REPLY3:",messages.message)
                #if action=="close": closeTrade(MyOrders[t].orderid)
                #print("REPLY4:",messages.message)
                #print("Action:",action)

                #even=re.sub(r'.*even.*',r'even',messages.message,flags=re.DOTALL|re.IGNORECASE)
                #if action=="even": orderEven(t)
                #print("REPLY4:",messages.message)
                return
        print("-------------------------------------------------------")
    msg=messages.message
    print("=========================== ",messages.id,"======================")
    msg=msg.lower()
    msg=re.sub(r'[^\x00-\x7F]+',' ',msg)
    msg=re.sub(r'\(scalping\)','',msg)
    msg=re.sub(r'Signal Number[ :]*\d+','',msg,flags=re.IGNORECASE)
    msg=re.sub(r'Signal[-: ]+\d+','',msg,flags=re.IGNORECASE)
    msg=re.sub(r'#',' ',msg)
    msg=re.sub(r'\*',' ',msg)
    msg=msg.replace('\n',' ')
    msg=msg.replace('\r\n',' ')
    msg=msg.replace('...',' ')
    msg=msg.replace('..+',' ')
    msg=msg.replace('..',' ')
    msg=msg.replace('  ',' ')
    msg=msg.replace('  ',' ')
    msg=msg.replace(':',' ')
    msg=msg.replace(',',' ')
    msg=msg.replace('. ',' ')
    msg=msg.replace('/',' ')
    msg=msg.replace('(',' ')
    msg=msg.replace(')',' ')
    msg=msg.replace('|',' ')
    msg=msg.replace('sl at','sl')
    msg=msg.replace('tp at','tp')
    msg=msg.replace('stoploss','sl')
    msg=msg.replace('takeprofit','tp')
    msg=msg.replace('stop loss','sl')
    msg=msg.replace('take profit','tp')
    msg=msg.replace('tp for all','tp')
    msg=msg.replace('sl for all','sl')
    msg=msg.replace('\\',' ')
    msg=msg.replace(' cmp',' ')
    msg=msg.replace('@',' ')
    msg=re.sub(r'[\(\)\[\]{}\-]',' ',msg,flags=re.IGNORECASE)
    msg=re.sub(r'Risk *\d+ *(Pip|pips)',' ',msg)
    msg=re.sub(r'Reward *\d+ *(Pip|pips)',' ',msg)
    msg=re.sub(r'waves scout forex',' ',msg)
    msg=re.sub(r'all copyrights reserved',' ',msg)
    msg=re.sub(r'(.*)(buy|sell) (limit|stp)(.*)',r'\1 \2\3 \4',msg)
    msg=msg.strip()
    msg=msg.replace('  ',' ')
    msg=msg.replace('  ',' ')
    msg=msg.replace('  ',' ')
    msg=msg.replace('  ',' ')
    msg=msg.replace('  ',' ')
    msg=os.linesep.join([s for s in msg.splitlines() if s.strip()])
    print(msg)
    print("-------------------------------------------------------")
    if  pattern != "": 
        if re.match(pattern,messages.message,re.IGNORECASE) is not None:
            signal=1
    else:
        if re.match('.*(sell|buy).*',msg,re.IGNORECASE) is not None:
            signal=1
    if fwd_from !=0 and message.fwd_from != None and signal==1:
        print("signal fwd from checking")
        print(fwd_from,message.fwd_from)
        if re.search(str(fwd_from), str(message.fwd_from) ) is not None:
            print("signal fwd ok")
            signal=1
        else:
            print("signal fwd nok")
            signal=0
    if signal == 0:
        return()
    symbol=""
    x=msg.split(' ')
    typ=""
    print(x)
    c=0
    for t in range(0,len(x)):
        if re.match('.*(buy|sell).*',x[t]) != None:
            typ=x[t]
            break
    c=t
    for p in range(0,len(x)):
        if x[p].upper() in Symbols:
            symbol=x[p]
            break
    if symbol == "":
        for p in range(0,len(x)-1):
            if x[p].upper()+x[p+1].upper() in Symbols:
                symbol=x[p]+x[p+1]
                break
    at=0
    tp=0
    sl=0
    tps=""
    tp1=0
    tp2=0
    try:
        for t in range(c,len(x)):
            if match(rgx_price,x[t]) == x[t]:
                at=x[t]
                c=t+1
                break
        for t in range(c,len(x)):
            if re.match('.*(tp|takeprofit).*',x[t]) != None:
        #   if x[t] == "tp" :
#               w=1
#               if re.match('\w+',x[t+w]: w=w+1
                if match(rgx_price,x[t+1]) == x[t+1] or x[t+1] == "open":
                    if x[t+1]  == "open":
                        p=0
                    else:
                        p=x[t+1]
                        if float(tp1) != 0:
                            tp2=p
                            tp=tp2
                        else:
                            tp1=p
                            tp=tp1
                    tps=tps+","+str(x[t+1])
            #if re.match('.*(sl|stoploss).*',x[t]) != None:
            if x[t] == "sl":
                if match(rgx_price,x[t+1]) == x[t+1]:
                    sl=x[t+1]
                
    except:
        if DEBUG:  # Use some boolean to represent dev state, such as DEBUG in Django
            raise
        else:
            Error("order getting tp and sl  for msg:",x,msg,"channel:",cid,channels[ci])
            Error("original message",messages.message)
    try:
        dt= messages.date
        #if symbol == "gold": symbol="xauusd"
        if symbol == "oil": symbol="WTICO_USD"
        #if symbol == "nas100": symbol="US100"
        #if symbol == "nasdaq": symbol="US100"
        print("Extracted Order ",oc,":",dt,"SYM:",symbol,"typ:",typ,"at:",at,"sl:",sl,"tp:",tp,"tp1:", tp1, "tps",tps ,"dt:",dt)
        if tp == "open":
            tp=0
        Order=Orders(msgid=messages.id,symbol=symbol,type=typ,atprice=at,stoploss=sl,takeprofit=tp, tp1=tp1 ,dt=dt,origmsg=messages.message,channel_id=cid)
        if test:
            return(Order)
        if isSignalValid(Order,cid):
            MyOrders.append(Order)
            Notif("===ADDED",oc, describeOrder(len(MyOrders)-1))
            OrdersModified=1
            oc+=1
    except Exception as e:
        if DEBUG:  # Use some boolean to represent dev state, such as DEBUG in Django
            raise
        else:
            Error('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
            Error("order pars error for msg:",messages.id, "channel:",cid,channels[ci])















client = TelegramClient('session_name', api_id, api_hash)
#client.connect()
@client.on(events.NewMessage)
async def my_event_handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    chat_id = event.chat_id
    sender_id = event.sender_id
    message_id = event._message_id
    channel=chat.id

    print("=======================================")
    print("chat {}, \n sender {} ,\n chat_id {} ,\n sender_id {} ,\n msg {}\n ".format(type(chat),sender,chat_id,sender_id,event.raw_text))

    if event.is_channel():
        print("Channel yes")
        pars_message(event.message,cid=None,channel=chat)
    #print(dir(event))

    print("MESSAGE",dir(event.message))
    print("CHAT",dir(chat))
    print("MESSAGE",event.message.__dict__)
    print("CHAT",chat.__dict__)
    print("DICT EVENT",event.__dict__)
    print("DIR",dir(event))
    print("==#####################################")


    # 1 . get event -message 
    # 2 . check if it is a valid channel
    # 3 . check if it has a valid signal
    # 4 . extract the signal.
    # 5 . if it is update on a signal
    # 6 . submit signal and update to sigmanager
    

client.start()
client.run_until_disconnected()
