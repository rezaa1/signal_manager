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
from exampleauth import exampleAuth
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

class Orders:
    def __init__(self, msgid=0, orderid=0 , symbol="" , type="", atprice="", stoploss="", takeprofit="", tp1="" , dt=datetime.datetime.now(),origmsg = "", ordererr=0, ordererrmsg="", status=0, notified=0  , channel_id = "", units=0 , tradePL = 0 , tradepipsPL = 0,desc="", flags=[]):
        takeprofit=float(takeprofit)
        stoploss=float(stoploss)
        #if "_" not in symbol:
#        if len(symbol)  == 6 :
#        	if symbol[4] != "_":
#        		symbol=symbol.upper()[0:3]+"_"+symbol.upper()[3:]
        symbol=symbol.upper()
        if symbol != "":
            symbol=Oanda[Symbols.index(symbol)]
        self.symbol=symbol
        self.msgid = msgid
        self.type = type
        self.stoploss = stoploss
        self.atprice = atprice
        self.takeprofit = takeprofit
        if float(tp1) != float(takeprofit):
         self.tp1 = tp1
        else:       
         self.tp1 = 0
        self.comment = ""
        self.msgdt = dt
        self.origmsg = origmsg
        self.ordererr = ordererr
        self.ordererrmsg = ordererrmsg
        self.notified = 0
        self.pipstotriger = 0

        self.units = units
        self.orderid = orderid
        self.PL = 0
        self.PLpips = 0
        self.channel_id  = channel_id
        self.tradePL  = 0
        self.tradepipsPL  = 0
        self.tradeRatio  = 0
        self.tradeOpenPrice  = 0

        self.live_units = 0
        self.live_orderid = 0
        self.live_PL = 0
        self.live_PLpips = 0
        self.live_PLpips = 0
        self.desc = desc
        self.flags = flags
        self.BE = 0
        try:
        	ratio=abs((float(atprice) - float(takeprofit) ) / ( float(atprice) - float(stoploss) ))
        	self.rrRatio="{0:.2f}".format(ratio)
        except:
             print("ratio calc error")	
             self.rrRatio="-1"
             pass
        self.status = status
        # status:
        # 0 New
        # 1 Active
        # 2 Pending
        # 3 Cancled
        # 4 Error
        # 9 Closed
#        self.opendt = opendt
#        self.closedt = closedt

class Channel:
    def __init__(self, name, link="",pars_func ="" , id=0,accountID="",signalpattern="",live_accountID="",live=0, risk=10, token="" , env="practice", lastmid=0 , size =0, manage=False,mpoints="", fwd_from=0,copy=0):
        self.name=name
        self.link =link
        self.id =id
        self.pars_func = pars_func
        self.accountID= accountID
        self.live_accountID= live_accountID
        self.live= live
        self.signalpattern= signalpattern
        self.risk= risk
        self.size= size
        self.token= token
        self.lastmid= lastmid
        self.environment= env
        self.PL = 0
        self.PLpips =0
        self.UPL = 0
        self.UPLpips =0
        self.manage = manage
        self.mpoints = mpoints
        self.fwd_from = fwd_from
        self.copy = copy

def get_symbols(db):

	oanda=db.all('select symbolvar.name,oanda from symbolvar, symbols where symbols.id = symbolvar.symbol_id',back_as=dict)
	for x in oanda:
		Symbols.append(x.get('name'))
		Oanda.append(x.get('oanda'))


def get_original_msgid(id,channel):
	rid=id
	msg=client.get_messages(channel,ids=id)
	if msg == None:
		return(rid)
	#print("0000-",id,":",msg,"-00000")
	if msg.reply_to_msg_id == None:
		if msg.id == None:
			print("GETORIG_Wierd, id,replyid",msg)
		rid=msg.id
	else:
		#print("GETORIG, id,replyid",id,msg.reply_to_msg_id)
		rid=get_original_msgid(msg.reply_to_msg_id,channel)
	return(rid)	


def load_var(name,chid):
	file=SaveDir+str(chid)+"_"+name+".save"
	myfile=Path(file)
	if myfile.is_file():
		fh=open(file,"r")
		val=fh.read()
		return val
	else:
		return "0"
def save_var(name,chid,val):
	file=SaveDir+str(chid)+"_"+name+".save"
	myfile=Path(file)
	fh=open(file,"w")
	fh.write(str(val))

def match(reg,var):
	r=re.match(reg,var)
	if r != None:
		r=r.group()
	return(r)
def pars_message(messages,cid,channel=None,test=False):
	global oc
	global OrdersModified
	rgx_price='((|\d)+\.\d+|\d+)'
	print("DBG in pars_message, cid:",cid)
	ci=getChannelAID(cid)
	print("DBG in pars_message, ci:",ci)

	ftype=channels[ci].pars_func
	pattern=channels[ci].signalpattern
	fwd_from=channels[ci].fwd_from
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
				#	sl= re.sub(r'.*sl [ a-z]*(\d+.\d+).*',r'\1',msg,flags=re.DOTALL|re.IGNORECASE)
				#	MyOrders[t].sl=sl
				#	if MyOrders[t].status < 3:
				#		updateTrade(t)
				
				

				
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
		#	if x[t] == "tp" :
#				w=1
#				if re.match('\w+',x[t+w]: w=w+1
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

def closeTrade(order,half=0,flag=""):
	global OrdersModified
	caid=getChannelAID(MyOrders[order].channel_id)
	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment

	if flag != "": 
		if flag in MyOrders[order].flags:
			return 0

	if MyOrders[order].orderid == 0 and int(MyOrders[order].status) in [0, 2]:
		MyOrders[order].comment=MyOrders[order].comment+"Cancel Order as it is not active yet, and close action is deffiend"
		cancelOrder(order)
		OrdersModified=1
		Notif("Cancel Order as it is not active yet",describeOrder(order))
		return()
	if MyOrders[order].status != 1:
		Notif("Order  status is not active ",describeOrder(order))

	api = oandapyV20.API(environment=env,access_token=token)
	from oandapyV20.contrib.requests import TradeCloseRequest
	import oandapyV20.endpoints.trades as trades
#	ordr = TradeCloseRequest(units=10000)
	if half==1:
		units=abs(round(int(MyOrders[order].units)/2))
		MyOrders[order].comment=MyOrders[order].comment+": Close half trade,"
		data={ "units": str(units) }
		r = trades.TradeClose(accountID=account, tradeID=int(MyOrders[order].orderid),data=data)
		Notif("Order close half -done ",describeOrder(order))
	else:
		units=abs(float(MyOrders[order].units))
		MyOrders[order].comment=MyOrders[order].comment+": Close trade,"
		r = trades.TradeClose(accountID=account, tradeID=int(MyOrders[order].orderid))
		Notif("Order close -done ",describeOrder(order))
	try:
    	# create the OrderCreate request
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		print("ERROR in close trade",err)
		MyOrders[order].ordererrmsg=find_key(err,'errorMessage')
		MyOrders[order].comment=MyOrders[order].comment+"failed"
		Error(__name__,find_key(err,'errorMessage'))
	else:
		print("____")
		print(json.dumps(rv, indent=2))
		if half==1:
			MyOrders[order].units=int(MyOrders[order].units) - units
			MyOrders[order].notified=0 
		else:
			#MyOrders[order].status=9
			MyOrders[order].notified=0 
		if flag != "": MyOrders[order].flags.append(flag)
		MyOrders[order].comment=MyOrders[order].comment+"done"
		Notif("Order action -done ",describeOrder(order))
	OrdersModified=1




def getSymbolPipValue(symbol):
	multiplier=0
	for c in range(0,len(Instrumentspip)):
		if Instrumentspip[c]["symbol"] == symbol:
			multiplier=float(Instrumentspip[c]["pip"])
			break
	if multiplier == 0: 
		Error("pipcalc",sym, "not found")
	return(multiplier)

def pipCalc(open: float, close: float,symbol:str):

	multiplier=getSymbolPipValue(symbol)
#	for c in range(0,len(Instrumentspip)):
#		if Instrumentspip[c]["symbol"] == sym:
#			multiplier=float(Instrumentspip[c]["pip"])
#			break

	if multiplier == 0: 
		Error("pipcalc",sym, "not found")
		return(0)
	pips = round((close - open) / multiplier)
	#print("pipc,sym:",sym,"multip:",multiplier,"p",close,open,pips)
	return int(pips)

def pendingOrder(order):

	global OrdersModified
	caid=getChannelAID(MyOrders[order].channel_id)
	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment
	at = float(MyOrders[order].atprice)
	tp=float(MyOrders[order].takeprofit)
	sym=MyOrders[order].symbol
	units=MyOrders[order].units
	api = oandapyV20.API(environment=env,access_token=token)

	Notif("preparing to put pending order",describeOrder(order))
	if MyOrders[order].status!=0:
		Error("order status is not coorect")
		return(0)
	if re.match("sell",MyOrders[order].type,re.IGNORECASE) is not None:
		direction=-1
	if re.match("buy",MyOrders[order].type,re.IGNORECASE) is not None:
		direction=1
	price=float(getPrice(sym,direction))

	stoporder=0
	if direction == 1:
		if not price > at:
			limitorder=1
		else:
			stoporder=1
	else:
		if price < at:
			limitorder=1
		else:
			stoporder=1

	if tp != 0: 
		takeProfitOnFill=TakeProfitDetails(price=tp).data
	else:
		takeProfitOnFill=None

	if stoporder == 1:
		ordr = StopOrderRequest(instrument=MyOrders[order].symbol,units=units, price=at,takeProfitOnFill=takeProfitOnFill, stopLossOnFill=StopLossDetails(price=MyOrders[order].stoploss).data )
	else:
		ordr = LimitOrderRequest(instrument=MyOrders[order].symbol,units=units, price=at,takeProfitOnFill=takeProfitOnFill, stopLossOnFill=StopLossDetails(price=MyOrders[order].stoploss).data )

	r = orders.OrderCreate(accountID=account, data=ordr.data)
	try:
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		Error(r.status_code, err)
		MyOrders[order].status=4
	else:
		MyOrders[order].comment=MyOrders[order].comment+":Pending Order ,ok"
		MyOrders[order].orderid=rv["orderCreateTransaction"]["id"]
		MyOrders[order].status=2

		print(json.dumps(rv, indent=2))
		canceled=find_key(rv,"orderCancelTransaction")
		print("____")
		try:
			cancelReason=rv["orderCancelTransaction"]["reason"]
			MyOrders[order].comment=MyOrders[order].comment+":Trade Update,cancle reason:"+cancelReason
		except:
			pass	
	OrdersModified=1


def cancelOrder(order=0,orderID=0,channel=0):

	global OrdersModified
	if order == 0:
		caid=channel
		oid=orderID
	else:
		oid=MyOrders[order].orderid
		caid=getChannelAID(MyOrders[order].channel_id)

	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment
	api = oandapyV20.API(environment=env,access_token=token)

	if int(oid) == 0:
		Notif("not pending order")
		MyOrders[order].status=3
		return()

	r = orders.OrderCancel(accountID=account, orderID=oid)
	try:
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		Error(r.status_code, err)
	else:
		if order != 0:
			MyOrders[order].comment=MyOrders[order].comment+":cancel,ok"
			MyOrders[order].status=3
			Notif("Cancel Order",describeOrder(order))
		print(json.dumps(rv, indent=2))
		Error("Cancel order ", oid)
		try:
			cancelReason=rv["orderCancelTransaction"]["reason"]
			if order != 0:
				MyOrders[order].comment=MyOrders[order].comment+":Trade Update,cancle reason:"+cancelReason

		except:
			pass	
	OrdersModified=1




def putOrder(order):
		
	if int(MyOrders[order].orderid) !=0:
		Error("Order id not 0, no order/trade should be created",describeOrder(order))	
		return()
	global OrdersModified
	caid=getChannelAID(MyOrders[order].channel_id)
	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment
	try:
		at = float(MyOrders[order].atprice)
	except:
		Error("converting at price",MyOrders[order].atprice,describeOrder(order))
		pass
	api = oandapyV20.API(environment=env,access_token=token)

	devide=1
#	if int(MyOrders[order].tp1) != 0: devide=2 

#	if  o == 0:
	tp=MyOrders[order].takeprofit
#	else:
#		tp=MyOrders[order].tp1

	Notif( "preparing to put order for :",order)
	if re.match("sell",MyOrders[order].type,re.IGNORECASE) is not None:
		direction=-1
	if re.match("buy",MyOrders[order].type,re.IGNORECASE) is not None:
		direction=1
	if float(MyOrders[order].atprice) != 0:
		rate=getPriceDetail(MyOrders[order].symbol,order=order)
		if direction > 0:
			price=float(rate['bid'])
		else:
         		price=float(rate['ask'])

		pips=pipCalc(at,price,MyOrders[order].symbol)
		if abs(pips) > 3:
			MyOrders[order].pipstotriger=pips
			factor=float(rate["quoteHomeConversionFactor"])
			units=round(risk/(factor*abs(float(MyOrders[order].stoploss) - float(MyOrders[order].atprice))))
			units=units*direction	
			MyOrders[order].units=units
			pendingOrder(order)
			return
	else:
		return
	Notif(describeOrder(order),"CurrentP:",price,"pip:",pips)
	factor=float(rate["quoteHomeConversionFactor"])
	units=round(risk/(factor*abs(float(MyOrders[order].stoploss) - float(price))))
	units=units*direction	
	MyOrders[order].units=units
	if tp == 0:
		mktOrder = MarketOrderRequest(
		instrument=MyOrders[order].symbol,
		units=units,
		clientExtensions=ClientExtensions(clientID=str(MyOrders[order].msgid),clientComment=str(MyOrders[order].msgid)).data,
		stopLossOnFill=StopLossDetails(price=MyOrders[order].stoploss).data)
	else:
		mktOrder = MarketOrderRequest(
		instrument=MyOrders[order].symbol,
		units=units,
		clientExtensions=ClientExtensions(clientID=str(MyOrders[order].msgid),clientComment=str(MyOrders[order].msgid)).data,
		takeProfitOnFill=TakeProfitDetails(price=tp).data,
		stopLossOnFill=StopLossDetails(price=MyOrders[order].stoploss).data)

# create the OrderCreate request
	oid=0
	print("S1")
	r = orders.OrderCreate(accountID=account, data=mktOrder.data)
	print("S2")
	try:
    	# create the OrderCreate request
		rv = api.request(r)
		print("S3")
	except oandapyV20.exceptions.V20Error as err:
		Error(r.status_code, err)
		print("S4")
		MyOrders[order].status=4
		MyOrders[order].ordererr=r.status_code
		MyOrders[order].ordererrmsg=err["orderRejectTransaction"]["rejectReason"]
		Error(r.status_code, err, "===>" , MyOrders[order].ordererrmsg)
	else:
		print("S5")
		print(json.dumps(rv, indent=2))
		print("____")
		#res=json.loads(json.dumps(rv))
		#canceled=find_key(rv,"orderCancelTransaction")
		print("____")
		try:

			print("S6")
			cancelReason=rv["orderCancelTransaction"]["reason"]
			Error("cancled order:",describeOrder(order),cancelReason)
			MyOrders[order].status=3
			MyOrders[order].ordererrmsg=cancelReason
		except:
			pass	
		
		try:
			print("S7")
			#fillOrder=rv["orderFillTransaction"]["orderID"]
			fillOrder=rv["orderFillTransaction"]["tradeOpened"]["tradeID"]
			MyOrders[order].status=1
			MyOrders[order].orderid=fillOrder
			Notif("Done",fillOrder)
		except:
			pass	
	OrdersModified=1
#=====================================

def describeOrder(order):
	try:
		PT = PrettyTable()
		t=order
		status=MyOrders[t].status
		dt=MyOrders[t].msgdt
		if isinstance(dt , str):
			dt=datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S+00:00')

		if status in [0,2]:
			PT.field_names = ["id","msgid","status","channel_id","ChannelName","dt","symbol","type","at","stoploss","takeprofit","pipstotriger","RRR"]
			PT.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,MyOrders[t].takeprofit,MyOrders[t].pipstotriger,MyOrders[t].rrRatio])
		elif status == 1:
			PT.field_names = ["id","msgid","status","channel_id","ChannelName","dt","symbol","type","at","stoploss","takeprofit","TP1","RRR","Units","PLpips","orderid","tradePL","Tratio"]
			PT.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,MyOrders[t].takeprofit,MyOrders[t].tp1,MyOrders[t].rrRatio,round(MyOrders[t].units),MyOrders[t].PLpips,MyOrders[t].orderid,"{0:.2f}".format(MyOrders[t].PL),MyOrders[t].tradeRatio])
		elif status in [3,4]:
			PT.field_names = ["id","msgid","status","channel_id","ChannelName","dt","symbol","type","at","stoploss","takeprofit","ERROR"]
			PT.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,MyOrders[t].takeprofit,MyOrders[t].ordererrmsg])
		elif status == 9:
			PT.field_names = ["id","msgid","status","channel_id","ChannelName","dt","symbol","type","at","stoploss","takeprofit","PLpips","orderid","tradePL"]
			PT.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,MyOrders[t].takeprofit,MyOrders[t].PLpips,MyOrders[t].orderid,str(MyOrders[t].PL)])
	#return(PT.get_string())
		ret=PT.get_string()
		ret="symbol: {} chname: {} typ:{} at: {} sl: {} tp: {} orderID:{} status: {} ".format(MyOrders[order].symbol, getChannelName(MyOrders[order].channel_id), MyOrders[order].type , MyOrders[order].atprice,MyOrders[order].stoploss,MyOrders[order].takeprofit,MyOrders[order].orderid,MyOrders[order].status)
	except:
		print("describe order error", order)
		ret=""
		pass
	return(ret)



def updateOpendOrder(order):

	global OrdersModified
	trans=getTransactions(order=order)
	oid=MyOrders[order].orderid
	found=0
	tid=""
	for c in range(0,len(trans)):
		tr=trans[c]
		if "orderID" in tr.keys():
			if int(tr["orderID"]) == int(oid):
				if tr['type'] != 'ORDER_CANCEL_REJECT': found=1
				print(tr)
				print(tr['type'])
				OrdersModified=1
				if tr["type"] == "ORDER_FILL":
					if "tradeOpened" in tr.keys():
						tid=tr["tradeOpened"]["tradeID"]
						status=1
						MyOrders[order].status=1
						MyOrders[order].orderid	= tid
						Notif("Order Activated ",describeOrder(order))
						break
					elif "tradeReduced" in tr.keys():
						tid=tr["tradeReduced"]["tradeID"]
					else:
						Notif("Order Activated  but this transaction is not correct",tr.keys())
				if tr["type"] == "ORDER_CANCEL":
					reason=tr["reason"]
					MyOrders[order].status=3
					MyOrders[order].comment=MyOrders[order].comment+":"+reason
					Notif("Order Cancled ",reason,describeOrder(order))
					break
	if found!=1:
		Error("pending order , no trans found, set signal as cancle ",describeOrder(order))
		#channels[MyOrders[order].channel_id].last_trans=trans[-1]['id']
		MyOrders[order].status=3
		OrdersModified=1
	else:
		Notif("pending order , trans found",describeOrder(order))
		if tid != "":
			MyOrders[order].status=1
			MyOrders[order].orderid = tid
			Notif(" set as active anyway tid:",tid)


def updateClosedTrade(order):

	global OrdersModified
	trans=getTransactions(order=order)
	oid=MyOrders[order].orderid
	found=0
	for c in range(0,len(trans)):
		tr=trans[c]
		if tr["type"] == "ORDER_FILL":
			if "tradesClosed"  in tr.keys():
				trc=tr["tradesClosed"][0]
				tid=trc["tradeID"]
				if tid==oid: 
					units=trc["units"]
					pl=trc["realizedPL"]
					price=trc["price"]
					costs=trc["financing"]
					trade_pl=tr["pl"]
					found=1
					break
	if found==1:
		MyOrders[order].PL=trade_pl				
		pip=abs(pipCalc(float(MyOrders[order].tradeOpenPrice),float(price),symbol=MyOrders[order].symbol))
		if float(trade_pl) < 0:
			pip=pip*-1
		MyOrders[order].PLpips=pip
		MyOrders[order].status=9
		Notif("Closed Trade",describeOrder(order),"realizedPL",trade_pl,"pl",pl)
		OrdersModified=1
	else:
		Error("Closed signal , no trans found",describeOrder(order))
		MyOrders[order].status=9
		OrdersModified=1



def getOrders(channel):


	import oandapyV20.endpoints.orders  as orders
	global OrdersrModified

	token=channels[channel].token
	account=channels[channel].accountID
	env=channels[channel].environment

	api = oandapyV20.API(environment=env,access_token=token)


	r = orders.OrderList(accountID=account)

	try:
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		print(r.status_code, err)
		return()
	else:
		#print(json.dumps(rv, indent=2))
		return(rv["orders"])

def getTransactions(order,fromID=1):

	global OrdersModified
	caid=getChannelAID(MyOrders[order].channel_id)
	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment

	api = oandapyV20.API(environment=env,access_token=token)

	import oandapyV20.endpoints.transactions  as otr
	trs=[]
	while True:
		param={ "id": fromID }
		r = otr.TransactionsSinceID(account,params=param)
		try:
			rv = api.request(r)
		except oandapyV20.exceptions.V20Error as err:
			Error("Getting transactions error:",r.status_code, err)
		tr=rv["transactions"]
		trs=trs+tr
		if len(tr) == 0:
			break
		else:
			fromID=int(tr[-1]['id'])
	return(trs)


def breakevenTrade(order,flag="BE",pips=2):

#	if flag in MyOrders[order].flags:
	if MyOrders[order].BE==1:
		return

	if int(MyOrders[order].units) < 0: 
		pips=pips*-1 
	mp=getSymbolPipValue(MyOrders[order].symbol)
	MyOrders[order].stoploss=str(round(float(MyOrders[order].tradeOpenPrice)+(pips*mp),4))
	ok=updateTrade(order)
	if ok==0:
		MyOrders[order].BE=1
		Notif("BE - ok" , describeOrder(order))
		MyOrders[order].flags.append(flag)

def updateTrade(order):
	global OrdersModified
	caid=getChannelAID(MyOrders[order].channel_id)
	risk=channels[caid].risk
	token=channels[caid].token
	account=channels[caid].accountID
	env=channels[caid].environment

	if MyOrders[order].orderid == 0:
		MyOrders[order].status=3
		MyOrders[order].comment=MyOrders[order].comment+":Order Update,not trade yet"
		OrdersModified=1
		return(-1)

	api = oandapyV20.API(environment=env,access_token=token)
	import oandapyV20.endpoints.trades as trades

	if MyOrders[order].takeprofit == 0:
		data={
		   "stopLoss": {
		     "timeInForce": "GTC",
		     "price": str(MyOrders[order].stoploss)
		  }
		}
	else:
		data={
		  "takeProfit": {
		    "timeInForce": "GTC",
		    "price": str(MyOrders[order].takeprofit)
		  },
		   "stopLoss": {
		     "timeInForce": "GTC",
		     "price": str(MyOrders[order].stoploss)
		  }
		}
	ok=1

	r = trades.TradeCRCDO(accountID=account,tradeID=MyOrders[order].orderid, data=data)
	try:
    	# create the OrderCreate request
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		Error(r.status_code, err)
	else:
		MyOrders[order].comment=MyOrders[order].comment+":Trade Update,ok"
		print(json.dumps(rv, indent=2))
		print("____")
		print("tid")
		#res=json.loads(json.dumps(rv))
		#canceled=find_key(rv,"orderCancelTransaction")
		print("____")
		ok=0
		try:
			cancelReason=rv["orderCancelTransaction"]["reason"]
			MyOrders[order].comment=MyOrders[order].comment+":Trade Update,cancle reason:"+cancelReason
			ok=1
		except:
			pass	
			ok=0
	OrdersModified=	1
	return(ok)



#=====================================
	
def jsonDefault(object):
	if (type(object)) is datetime.datetime:
		return object
	else:
		return object.__dict__

def find_key(data, search_key, out=None):
    """Find all values from a nested dictionary for a given key."""
    if out is None:
        out = []
    if isinstance(data, dict):
        if search_key in data:
            out.append(data[search_key])
        for key in data:
            find_key(data[key], search_key, out)
    return out

import json
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.exceptions import V20Error
from exampleauth import exampleAuth
import logging

logging.basicConfig(
    filename="log.out",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',
)
def isSignalValid(order,cid):
	# Check if it is already deffined
	if order.symbol == "":
		return(False)

	if order.type == "":
		return(False)

	if float(order.stoploss) == 0:
		return(False)

	for t in range(0,len(MyOrders)):
		if order.msgid == MyOrders[t].msgid and int(MyOrders[t].channel_id) == int(cid):
			print("order Already exists")
			return(False)
	# Check if price is not in range
	return(True)

def getPrice(symbol,direction,order=0):
	r=getPriceDetail(symbol,order=order)
	if direction > 0:
		return(r['bid'])
	else:
		return(r['ask'])
	
def getPriceDetail(symbol,order=0,cho=0):
	if cho == 0:
		if order != 0:
			for c in range(0,len(channels)):
				if channels[c].id == MyOrders[order].channel_id:
					cho=c
					break	
	import oandapyV20.endpoints.pricing as pricing
	params = { "instruments" : symbol}
	#print("getPD,channel",symbol,":",cho,"order",order)
	r = pricing.PricingInfo(accountID=channels[cho].accountID, params=params)
	api = oandapyV20.API(environment=channels[cho].environment,access_token=channels[cho].token)
	rv = api.request(r)
#    print(r.response)
#    print("===")
#    print(rv.keys())
	bid=rv["prices"][0]['bids'][0]['price']
	ask=rv["prices"][0]['asks'][0]['price']
#print(rv["prices"][0].keys())
	qhcf_n=rv["prices"][0]["quoteHomeConversionFactors"]['negativeUnits']
	return({"bid": bid, "ask": ask,"quoteHomeConversionFactor":qhcf_n})

def getTrades(channel):
	token=channels[channel].token
	account=channels[channel].accountID
	env=channels[channel].environment

	api = oandapyV20.API(environment=env,access_token=token)
	import oandapyV20.endpoints.trades as trades
	import oandapyV20.endpoints.positions as pos
	import oandapyV20.endpoints.transactions  as tr

	#accountIID="101-001-8394451-001"
	tradelist=None
	r = trades.OpenTrades(accountID=account)
	try:
		rv = api.request(r)
	except oandapyV20.exceptions.V20Error as err:
		print(r.status_code, err)
		Error("getTrades,error",channels[channel].name,err)
		#logging.error("getTrades,error",channels[channel].name,err)
	else:
		#print(json.dumps(rv, indent=2))
		tradelist=rv["trades"]
		return(tradelist) 

def updateOrdersStatus():
	# Get Orders and check thier status
	for c in range(0,len(channels)):
		orders=getOrders(c)
#		print(channels[c].name,"orders:",orders,":",type(orders))
		if type(orders) is  not list:
			Notif("not orders for " , channels[c].name)
			return()
		for o in range(0,len(MyOrders)):
			if int(MyOrders[o].channel_id) == channels[c].id and int(MyOrders[o].status) == 2:
				active=0
				for t in range(0,len(orders)):
					if int(orders[t]["id"]) == int(MyOrders[o].orderid):
						priceC=float(getPrice(orders[t]["instrument"],int(MyOrders[o].units)))
						pips=abs(pipCalc(float(MyOrders[o].atprice),priceC,MyOrders[o].symbol))
						MyOrders[o].pipstotriger=pips						
						active=1
				if active == 0:
					updateOpendOrder(o)
		for t in range(0,len(orders)):
			if "instrument" in orders[t].keys():
				oid=int(orders[t]["id"])
				sym=orders[t]["instrument"]
				typ=int(orders[t]["units"])
				#opentime=datetime.datetime.strptime(trades[t]["openTime"],'%Y-%m-%dT%H:%M:%S.$sZ')
				oid_found=0
				for p in range(0,len(MyOrders)): 
					if int(MyOrders[p].channel_id) == channels[c].id:
						if oid == int(MyOrders[p].orderid):
							oid_found=1
							oid=p
				if oid_found == 0:
					Error("looking for signal for oid",oid,":",sym,":",channels[c].name)
					cancelOrder(orderID=oid,channel=c)
					for p in range(0,len(MyOrders)): 
						if int(MyOrders[p].channel_id) == channels[c].id:
							direction=0
							if re.match("sell",MyOrders[p].type,re.IGNORECASE) is not None:
								direction=-1
							if re.match("buy",MyOrders[p].type,re.IGNORECASE) is not None:
								direction=1
							if int(MyOrders[p].orderid) == 0  and MyOrders[p].symbol ==sym and ( typ * direction ) > 0 :
								#Error("found signal",p,"for tid",oid,describeOrder(p))
								print(orders[t])
								try:
									sl=float(orders[t]["stopLossOnFill"]["price"])
									tp=float(orders[t]["takeProfitOnFill"]["price"])
									if sl == float(MyOrders[p].stoploss) and tp == float(MyOrders[p].takeprofit):
										Notif("alocate order",oid," to signal",p,"cstatus",MyOrders[p].status,"oid",MyOrders[p].orderid)
										MyOrders[p].status=2
										MyOrders[p].orderid=tid
								except:
									cancelOrder(orderID=oid,channel=c)
									pass

				else:
					#print("found signal tid",tid,":",sym,":",typ,opentime,channels[c].name,"signal",MyOrders[oid].symbol,MyOrders[oid].msgdt,"status",MyOrders[oid].status)
					if MyOrders[oid].status != 2:
						Error("Found incorrect status, for signal,",describeOrder(oid),"status:",MyOrders[oid].status,",Fixing it")
						MyOrders[oid].status = 2

def updateTradesStatus():
	# Get Trades and check thier status
	for c in range(0,len(channels)):
		trades=getTrades(c)
		for o in range(0,len(MyOrders)):
			if int(MyOrders[o].channel_id) == channels[c].id and int(MyOrders[o].status) == 1:
				active=0
				for t in range(0,len(trades)):
					if int(trades[t]["id"]) == int(MyOrders[o].orderid):
						pl=float(trades[t]["unrealizedPL"])+float(trades[t]["realizedPL"])
						MyOrders[o].PL=pl
						MyOrders[o].tradePL=pl
						priceO=float(trades[t]["price"])
						priceC=float(getPrice(trades[t]["instrument"],int(trades[t]["currentUnits"])))
						pips=abs(pipCalc(priceO,priceC,MyOrders[o].symbol))
						tp=0
						sl=0
						try:
							tp=float(trades[t]["takeProfitOrder"]["price"])
							sl=float(trades[t]["stopLossOrder"]["price"])
						except:
							pass
						p=0
						if pl > 0:
							p=abs(100*(priceO-priceC)/(priceO-tp))
						if pl < 0:
							p=abs(100*(priceO-priceC)/(priceO-sl))*-1
							pips=pips*-1
						MyOrders[o].tradeRatio="{0:.2f}".format(p)
						MyOrders[o].PLpips=pips
						MyOrders[o].tradepipsPL=pips
						MyOrders[o].tradeOpenPrice=priceO
						#print(describeOrder(o),"tpdif",tp,pipCalc(tp,float(MyOrders[o].takeprofit)),"sldif:",sl,pipCalc(sl,float(MyOrders[o].stoploss)))
						if channels[c].manage == True and pl > 0:
							BE=int(channels[c].mpoints["BE"])
#							print("Manage",o,":",p,pips)
							if p > BE and abs(pips) > BE  and "MBE" not in MyOrders[o].flags:
								
								Notif("getting to 20%, move to break even",describeOrder(o))
								breakevenTrade(o,flag="MBE", pips=5)	
						active=1
				if active == 0:
					updateClosedTrade(o)

		for t in range(0,len(trades)):
			tid=int(trades[t]["id"])
			sym=trades[t]["instrument"]
			typ=int(trades[t]["initialUnits"])
			opentime=trades[t]["openTime"]
			#opentime=datetime.datetime.strptime(trades[t]["openTime"],'%Y-%m-%dT%H:%M:%S.$sZ')
			tid_found=0
			for p in range(0,len(MyOrders)): 
				if int(MyOrders[p].channel_id) == channels[c].id:
					if tid == int(MyOrders[p].orderid):
						tid_found=1
						oid=p
			if tid_found == 0:
				print("looking for signal for tid",tid,":",sym,":",typ,channels[c].name)
				for p in range(0,len(MyOrders)): 
					if int(MyOrders[p].channel_id) == channels[c].id:
						direction=0
						if re.match("sell",MyOrders[p].type,re.IGNORECASE) is not None:
							direction=-1
						if re.match("buy",MyOrders[p].type,re.IGNORECASE) is not None:
							direction=1
						if int(MyOrders[p].orderid) == 0  and MyOrders[p].symbol ==sym and ( typ * direction ) > 0:
							#Error("found signal",p,"for tid",tid,describeOrder(p))
							sl=float(trades[t]["stopLossOrder"]["price"])
							tp=float(trades[t]["takeProfitOrder"]["price"])
							if sl == float(MyOrders[p].stoploss) and tp == float(MyOrders[p].takeprofit):
								Notif("alocate trade to signal",p,"cstatus",MyOrders[p].status)
								MyOrders[p].status=1
								MyOrders[p].orderid=tid
							#ans=input("s it correct order?")

			else:
				#print("found signal tid",tid,":",sym,":",typ,opentime,channels[c].name,"signal",MyOrders[oid].symbol,MyOrders[oid].msgdt,"status",MyOrders[oid].status)
				if MyOrders[oid].status != 1:
					Error("Found incorrect status, for signal,",describeOrder(oid),"status:",MyOrders[oid].status,",Fixing it")
					MyOrders[oid].status = 1

def getChannelAccountID(cid):
	for c in range(0,len(channels)):
		if int(channels[c].id) == int(cid):
			return(channels[c].accountID)

def getChannelAID(cid):

	for c in range(0,len(channels)):
		if int(channels[c].id) == int(cid):
			return(c)
	print("DBG getChannelAID no cid found for ",cid)
	return(0)
def getChannelName(cid):
	for c in range(0,len(channels)):
		if int(channels[c].id) == int(cid):
			return(channels[c].name)

def Error(*args):
	info="https://t.me/joinchat/AAAAAEnJ4c0ywoAhU9eATQ"
	print( "Error in func:",inspect.stack()[1].lineno, inspect.stack()[1].function)
	print( "Error msg:",args)
	client.send_message('mreza_tid', "lineno:"+str(inspect.stack()[1].lineno) + "in func:"+ str( inspect.stack()[1].function))
	client.send_message('mreza_tid', str(args) )

def Notif(*args):
	print( "Notif in func:",inspect.stack()[1].lineno, inspect.stack()[1].function)
	print(args)
	client.send_message('mreza_tid', str(args) )

#========================================

def saveOrders():

	global OrderFile
	global OrdersModified
	if OrdersModified == 1:
		print("save order m1 ")
		timestamp=datetime.datetime.now().strftime("%d-%m-%y-%H%M%S")
		backupfile=BackupDir+OrderFileName+"_"+timestamp+"_OM"
		copyfile(OrderFile,backupfile)
		OrdersModified = 0
		with open(OrderFile, 'wb') as fp:
			pickle.dump(MyOrders, fp,0)
		
		with open (OrderFile, 'rb') as fp:
    			MyOrdersTest = pickle.load(fp)

		if len(MyOrders) != len(MyOrdersTest):
			Error("OrderTest:Failed, Orders:",len(MyOrders),"Testload:",len(MyOrdersTest)) 
			with open(OrderFile, 'wb') as fp:
				pickle.dump(MyOrders, fp,0)
			with open("backup", 'wb') as fp:
				pickle.dump(MyOrders, fp,0)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def setNewAttr(order):
        MyOrders[order].BE = 0
#        MyOrders[order].live_orderid = 0
#        MyOrders[order].live_PL = 0
#        MyOrders[order].live_PLpips = 0


def printOrders(active=0,pending=0,cancled=0,closed=0,channel=1):
	PTactive = PrettyTable()
	PTpending = PrettyTable()
	PTclosed = PrettyTable()
	PTcancled = PrettyTable()
	PTchannels = PrettyTable()
	SWactive = 0
	SWpending = 0
	SWcncled = 0
	SWclosed = 0
	PTpending.field_names = ["id","msgid","s","channel_id","ChName","dt","symbol","type","at","SL","TP","pipstotriger","RRR"]
	PTactive.field_names = ["id","msgid","s","channel_id","ChName","dt","symbol","type","at","SL","TP","TP1","RRR","Units","PLpips","orderid","tradePL","Tratio","flags"]
	PTcancled.field_names = ["id","msgid","s","channel_id","ChName","dt","symbol","type","at","SL","TP","ERROR"]
	PTclosed.field_names = ["id","msgid","s","channel_id","ChName","dt","symbol","type","at","SL","TP","PLpips","orderid","tradePL"]
	PTchannels.field_names = ["name","id","Profit/Loss","Profit/Loss pips","UPL","UPL pips","win rate"]

	for c in range(0,len(channels)):
		channels[c].PL=0
		channels[c].PLpips=0
		channels[c].UPL=0
		channels[c].UPLpips=0

	for t in range(0,len(MyOrders)):
		#if 1 == 1:
		try:	
			status=MyOrders[t].status
			caid=getChannelAID(MyOrders[t].channel_id)
			dt=MyOrders[t].msgdt
			tp=str(MyOrders[t].takeprofit)
			tp1=str(MyOrders[t].tp1)
			if tp1 != "":
				tps=tp+","+tp1
			else:
				tps=tp
			if isinstance(dt , str):
				dt=datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S+00:00')
			if status in [0,2]:
				PTpending.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,tp,MyOrders[t].pipstotriger,MyOrders[t].rrRatio])
				SWpending=1
			elif status == 1:
				PTactive.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,tp,tp1,MyOrders[t].rrRatio,round(MyOrders[t].units),MyOrders[t].PLpips,MyOrders[t].orderid,"{0:.2f}".format(MyOrders[t].PL),MyOrders[t].tradeRatio,''.join(MyOrders[t].flags)])
				SWactive=1
				channels[caid].UPL=MyOrders[t].PL+channels[caid].UPL
				channels[caid].UPLpips=MyOrders[t].PLpips+channels[caid].UPLpips
			elif status in [3,4]:
				PTcancled.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,tp,MyOrders[t].ordererrmsg])
				SWcancled=1
			elif status == 9:
				PTclosed.add_row([t,MyOrders[t].msgid,MyOrders[t].status,MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),dt.astimezone(get_localzone()).strftime("%m-%d %H:%M"),MyOrders[t].symbol,MyOrders[t].type,MyOrders[t].atprice,MyOrders[t].stoploss,tp,MyOrders[t].PLpips,MyOrders[t].orderid,str(MyOrders[t].PL)])
				channels[caid].PL=float(MyOrders[t].PL)+float(channels[caid].PL)
				channels[caid].PLpips=MyOrders[t].PLpips+channels[caid].PLpips
				SWclosed=1

		#else:
		except Exception as e:
			print('printORder , Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)),t)

	for c in range(0,len(channels)):
		channels[c].PL=round(channels[c].PL,2)
		channels[c].UPL=round(channels[c].UPL,2)
		w=0
		l=0
		for t in range(0,len(MyOrders)):
			if MyOrders[t].channel_id == channels[c].id and MyOrders[t].status ==9: 
				if float(MyOrders[t].PL) > 0: w=w+1		
				if float(MyOrders[t].PL) < 0: l=l+1		
		
		wlr=0
		if w+l > 0:
			wlr=round(w*100/(w+l),2)
		PTchannels.add_row([channels[c].name,channels[c].id,channels[c].PL,channels[c].PLpips,channels[c].UPL,channels[c].UPLpips,str(w)+"/"+str(l)+"="+ str(wlr)+"%" ])

	if active == 1 and SWactive == 1: print(PTactive)	
	if pending == 1 and SWpending == 1: print(PTpending)	
	if cancled == 1 and SWcancled == 1: print(PTcancled)	
	if closed == 1 and SWclosed == 1: print(PTclosed)	
	if channel == 1: print(PTchannels)	
#========================================


from telethon import TelegramClient, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, InputPeerUser, InputPeerChat, InputPeerChannel
import re
import pickle
import time
get_symbols(db)
 # These example values won't work. You must get your own api_id and
  # api_hash from https://my.telegram.org, under API Development.


# just for readability


sw=0
api_id = 198093
api_hash = 'b09413bcaefe07a147334e8855acdb27'

savedir="/root/tel/save/"

phone = '+61424908366'
username = 'mreza_tid'
client = TelegramClient('session_name', api_id, api_hash)
global MyOrders
client.connect()

# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

me = client.get_me()

client.send_message('mreza_tid', 'Hello! Starting telauto now')
oc=0


api = oandapyV20.API(access_token=access_token)

#print(client.get_me().stringify())


#client.get_dialogs()
global channels
channels=[]

channels.append(Channel(name="afinitoVIP",id=1377311260,pars_func="x",accountID="001-011-1957873-005",risk=10,token=access_token_live,env="live"))
channels.append(Channel(name="waveScout",id=1093697024,pars_func="x",accountID="001-011-1957873-006",signalpattern=".*signal +number.*",risk=10,token=access_token_live,env="live", size=10000))
#channels.append(Channel(name="queen",   id=1061651336,pars_func="x",accountID="001-011-1957873-004",risk=5,signalpattern=".*#[A-Za-z].*",token=access_token_live,env="live",manage=True,mpoints={"BE":"40"}))
channels.append(Channel(name="ETAPAID",id=1267437768,pars_func="x",accountID="001-011-1957873-007",risk=1,token=access_token_live,env="live",manage=True,mpoints={"BE":"20","T1":"30","T2":"50"}))
#channels.append(Channel(name="MYTrades",id=1415922072,pars_func="x",accountID="001-011-1957873-008",risk=1,token=access_token_live,env="live",signalpattern=""))
#channels.append(Channel(name="EverytmFx_L",id=1093875227,pars_func="x",accountID="001-011-1957873-009",risk=5,token=access_token_live,env="live",copy=1))
channels.append(Channel(name="Scorpions PREMIUM",id=1205448237,pars_func="x",accountID="001-011-1957873-010",risk=5,token=access_token_live,env="live"))

channels.append(Channel(name="LGT_FREE",id=1247469456,pars_func="x",accountID="101-001-8394451-009",signalpattern=".*signal-[0-9]+.*",risk=10,token=access_token))
channels.append(Channel(name="dutchVIP",id=1053761964,pars_func="x",accountID="101-001-8394451-005",risk=10,token=access_token))
channels.append(Channel(name="FXBlast",id=1186193542,pars_func="x",accountID="101-001-8394451-011",risk=5,token=access_token,signalpattern=""))
channels.append(Channel(name="EverytmFx",id=1093875226,pars_func="x",accountID="101-001-8394451-012",risk=5,token=access_token,signalpattern=""))
channels.append(Channel(name="SureFx",id=1310588184,pars_func="x",accountID="101-001-8394451-013",risk=5,token=access_token,signalpattern=""))
channels.append(Channel(name="GreenFx",id=1155317612,pars_func="x",accountID="101-001-8394451-014",risk=5,token=access_token,signalpattern=""))
channels.append(Channel(name="AccurateS",id=1178200863,pars_func="x",accountID="101-001-8394451-015",risk=5,token=access_token,signalpattern=""))
channels.append(Channel(name="FXStreet",id=1272029550,pars_func="x",accountID="101-001-8394451-017",risk=5,token=access_token,fwd_from=1334227287))
channels.append(Channel(name="FXLAB",id=1222450710,pars_func="x",accountID="101-001-8394451-016",risk=5,token=access_token))
channels.append(Channel(name="ProfitsWUs",id=1250116014,pars_func="x",accountID="101-001-8394451-018",risk=5,token=access_token))
channels.append(Channel(name="DragonFX",id=1165983517,pars_func="x",accountID="101-001-8394451-019",risk=5,token=access_token))
channels.append(Channel(name="FxMasterLvls",id=1298818082,pars_func="x",accountID="101-001-8394451-020",risk=5,token=access_token))

channels.append(Channel(name="FOXFPAIDTRIAL",id=1154319884,pars_func="x",accountID="101-011-11132956-003",risk=5,token=access_token_democrm))
channels.append(Channel(name="Authentic",id=1276317917,pars_func="x",accountID="101-011-11132956-004",risk=5,token=access_token_democrm))
channels.append(Channel(name="Aussie",id=1154517933,pars_func="x",accountID="101-011-11132956-005",risk=5,token=access_token_democrm))
channels.append(Channel(name="Put_Forget_ST",id=1066814774,pars_func="x",accountID="101-011-11132956-006",risk=5,token=access_token_democrm))
channels.append(Channel(name="FX HEROES",id=1167625455,pars_func="x",accountID="101-011-11132956-007",risk=5,token=access_token_democrm))
channels.append(Channel(name="Quantitative Analyst",id=1382856068,pars_func="x",accountID="101-011-11132956-008",risk=5,token=access_token_democrm))
channels.append(Channel(name="Eagle Fx",id=1288384244,pars_func="x",accountID="101-011-11132956-009",risk=5,token=access_token_democrm))
channels.append(Channel(name="Perfect signal",id=1348616823,pars_func="x",accountID="101-011-11132956-010",risk=5,token=access_token_democrm))
channels.append(Channel(name="TRADADEX",id=1376687278,pars_func="x",accountID="101-011-11132956-011",risk=5,token=access_token_democrm))
channels.append(Channel(name="UK PROFESSIONAL",id=1149970736,pars_func="x",accountID="101-011-11132956-012",risk=5,token=access_token_democrm))
channels.append(Channel(name="Signals Point",id=1120189408,pars_func="x",accountID="101-011-11132956-013",risk=5,token=access_token_democrm))
channels.append(Channel(name="Forex Premium",id=1242039981,pars_func="x",accountID="101-011-11132956-014",risk=5,token=access_token_democrm))
channels.append(Channel(name="Crystal Forex",id=1375827568,pars_func="x",accountID="101-011-11132956-015",risk=5,token=access_token_democrm))
channels.append(Channel(name="UK Forex Research",id=1292582342,pars_func="x",accountID="101-011-11132956-016",risk=5,token=access_token_democrm))
channels.append(Channel(name="FX ScöŕpìoNs",id=1269006602,pars_func="x",accountID="101-011-11132956-017",risk=5,token=access_token_democrm))
channels.append(Channel(name="Grando pip",id=1084020780,pars_func="x",accountID="101-011-11132956-018",risk=5,token=access_token_democrm))
channels.append(Channel(name="Affix Trade Captain",id=1276076231,pars_func="x",accountID="101-011-11132956-019",risk=5,token=access_token_democrm))
channels.append(Channel(name="Leärn to Träde",id =1326627704,pars_func="x",accountID="101-011-11132956-020",risk=5,token=access_token_democrm))

channels.append(Channel(name="Horizon Forex",id=1355784993,pars_func="x",accountID="101-011-11296588-002",risk=5,token=access_token_demobom))
channels.append(Channel(name="FINIVO FOREX",id=1316015931,pars_func="x",accountID="101-011-11296588-003",risk=5,token=access_token_demobom))
channels.append(Channel(name="Genius4x",id=1184989515,pars_func="x",accountID="101-011-11296588-004",risk=5,token=access_token_demobom))
channels.append(Channel(name="MegamindFx signal",id=1131755294,pars_func="x",accountID="101-011-11296588-005",risk=5,token=access_token_demobom))

for c in range(0,len(channels)):
	channels[c].lastmid=int(load_var("lastmid",channels[c].id,))

global MyOrders
MyOrders=[]
try:
	with open (OrderFile, 'rb') as fp:
    		MyOrders = pickle.load(fp)
	
except:
	Error("not able to open orders file, exiting")
	exit(28)

act=0
can=0
cls= 0
pen=0
for c in range(0,len(MyOrders)):
	if MyOrders[c].status in [1]: act+=1;
	if MyOrders[c].status in [0,2]: pen+=1;
	if MyOrders[c].status in [3,4]: can+=1;
	if MyOrders[c].status in [9]: cls+=1;

Notif("Number of Orders ," , len(MyOrders), "Pending:",pen,"Active:", act,"Canceld/Error:",can,"Close:",cls)

if len(MyOrders) < 10:
	Error("less than 10 orders loaded in My Orders, exxiting")
	exit(28)

while True:
	with open("/root/tel/save/.run", 'wt') as f:
		f.write("ok") 
	phone = '+61424908366'
	username = 'mreza_tid'
	print("starting new loop:",datetime.datetime.now())
	for c in range(0,len(channels)):
		try:
			client.get_dialogs()
			channel=client.get_entity(PeerChannel(channels[c].id-channels[c].copy))
		except Exception as e:
			Error('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
			Error("timeout")
			client.disconnect()
			exit()
			
		cid=str(channels[c].id)
		lastmid=channels[c].lastmid

		messages=client.get_messages(channel,1)
		message=messages[0]
		ilimit=0

		if lastmid != 0 :
			ilimit=message.id - lastmid
		else:
			Error("EER , lastmid = 0 ",c)
			ilimit=50
		if ilimit < 0:
			print("iilimit is negative for " ,channels[c].name,ilimit)
			ilimit=0
		print("channelname,id=>",channels[c].name,channel.id,"ilimit:",ilimit,"last msg:",lastmid)
		lastmid=message.id
		channels[c].lastmid=message.id

		try:
			allmessages = client.get_messages(channel,limit=ilimit)
		except Exception as e:
			print('Error!  get messagr Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)),t)
			print("error get message",ilimit,lastmid)
		print("lenm:",len(allmessages))
		for x in range(len(allmessages)-1,-1,-1):
			print(x)
			try:
				pars_message(allmessages[x],channels[c].id,channel)
			except Exception as e:
				if DEBUG:  # Use some boolean to represent dev state, such as DEBUG in Django
					raise           
				else:
					Error('Error!  pars_message Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
			

		save_var("lastmid",str(channels[c].id),str(lastmid))
	saveOrders()
	try: 
		print("getorderupdates..")
		updateOrdersStatus()
		print("gettradeupdates..")
		updateTradesStatus()
		print("done.")
	except Exception as e:
		Error('Error!  get order/trade update Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))

	for t in range(0,len(MyOrders)):
		#setNewAttr(t)
		status=MyOrders[t].status


		if MyOrders[t].status in [0,1,2]: 
			print("DBG " , describeOrder(t))
			print("DBG _ orders to check chid,msgid:" , MyOrders[t].channel_id,MyOrders[t].msgid)
			try:
				message=client.get_messages(MyOrders[t].channel_id,ids=MyOrders[t].msgid)
				print("DBG _ message:" , message)
				print("DBG _ chid" , MyOrders[t].channel_id)
				print(describeOrder(t))
				if message == None:
					print("no message with id",MyOrders[t].msgid)
				else:
					testorder=pars_message(message,cid=MyOrders[t].channel_id,test=True)
					print("DBG test order",testorder)
					if testorder != None:
						if testorder.symbol == MyOrders[t].symbol  and testorder.type ==  MyOrders[t].type:
							print(describeOrder(t),"validated")
						else:
							print(describeOrder(t),"not validated")
							print("test Orer",testorder)
					else:
						print("no order retruned")
			except:
				print("DBG _ error ")
				pass
		if not (status == 9 or (status >= 3  )):
			try:
				#rate=getPriceDetail(MyOrders[t].symbol,order=t)
				#factor=float(rate["quoteHomeConversionFactor"])
				#print(MyOrders[t].symbol,"facter",factor,"pipv",getSymbolPipValue(MyOrders[t].symbol))
				if MyOrders[t].status in [0,2]: 
					if sw == 0 and INTERACTIVE == 1 :
						try:
							at=float(MyOrders[t].atprice)
						except Exception as e:
							Error(e)
							at=0
							pass	
						price=float(getPrice(MyOrders[t].symbol,1))
						print("====================================================================")
						print(MyOrders[t].origmsg)
						print("---------------------------------")
						print(MyOrders[t].comment)
						print("-----------------------------------------------------------------")
						MyOrders[t].pipstotriger=pipCalc(at,price,MyOrders[t].symbol)
						print(describeOrder(t))
						print(MyOrders[t].symbol,":",MyOrders[t].status,":",getChannelName(MyOrders[t].channel_id),MyOrders[t].type,MyOrders[t].msgdt,"AT:",MyOrders[t].atprice,"CurrentP:",price,"SL:",MyOrders[t].stoploss,"TP:",MyOrders[t].takeprofit,"Pips to:",MyOrders[t].pipstotriger,"tid:",MyOrders[t].orderid,"PL:",MyOrders[t].PL,"PLpips:",MyOrders[t].PLpips,"percent:",MyOrders[t].tradePL,"RRR:",MyOrders[t].rrRatio)
						c=input("cancel order?")
						if c == "y":
							cancelOrder(t)
						else:
							if int(MyOrders[t].status) ==  0: putOrder(t)
					else:
						if int(MyOrders[t].status) ==  0: putOrder(t)
				elif status == 1:
					if float(MyOrders[t].tp1) and "TP1" not in MyOrders[t].flags  != 0:
						price=float(getPrice(MyOrders[t].symbol,1))
						if abs(pipCalc(float(MyOrders[t].tp1),price,MyOrders[t].symbol)) < 2:
							Notif("tp1 - done  , c;osing half",describeOrder(t))
							closeTrade(t,1,flag="TP1")
							Notif("breakeven the trade")
							breakevenTrade(t)
							
				elif status == 3:
					MyOrders[t].notified=1
					print("--",MyOrders[t].msgid,"==" ,status,"Err:",MyOrders[t].ordererr,"EMsg:",MyOrders[t].ordererrmsg)
			except Exception as e:
				Error(e)
				Error("Sig(",MyOrders[t].msgid,",",MyOrders[t].status,"ch_",MyOrders[t].channel_id,getChannelName(MyOrders[t].channel_id),"):",t,"-",MyOrders[t].msgdt,"SYM:",MyOrders[t].symbol,"Typ:",MyOrders[t].type,"AT:",MyOrders[t].atprice,"SL:",MyOrders[t].stoploss,"TP:",MyOrders[t].takeprofit,"Pips to:",MyOrders[t].pipstotriger)
				Error("error on order "+str(t)+MyOrders[t].origmsg)
				MyOrders[t].status=4
			#print("====================================")

	sw=1
	saveOrders()
	printOrders(active=1,pending=1,cancled=0,closed=0)
	print( "Press any key to exit or wait 60 seconds...")
	c=""
#	timeout = 60
#	rlist, wlist, xlist = select([sys.stdin], [], [], timeout)
#	if rlist:
#		print ("exit selected...:",rlist)
#		break
	time.sleep(50)
	
client.disconnect()
exit(10)
# Reset the terminal:
#data = load(, Loader=Loader)

#		else:
#			if messages.reply_to_messages.message_id is not 'None':
#				print(messages.message)
#				messages = client.get_messages(channel,ids=messages.reply_to_messages.message_id)
#				print(messages.message)
#messages = client.get_messages('Mali_Hb')

#x=client.GetFullChannelRequest
#print(x)

#result = client.get_messages.ChatFull('Mali_Hb')
#print(result)


