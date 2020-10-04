from trades.error import *


from django.apps import AppConfig
from oanda.models import Instrument

import oandapyV20
import oandapyV20.endpoints.accounts as accounts

import json
import oandapyV20.endpoints.pricing as pricing

#from trades.apps import check_pending_orders
#---
from django.apps import AppConfig
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from signals.models import Signal
from django.db.models import Exists,OuterRef
from trades.models import Trade
from signals.serializers import SignalSerializer
from signals.models import Bot
from signals.models import Channel
from signals.models import MessageRecord
from trades.models import Account, Follower, Strategy, Broker
from oanda.models import Instrument
from telegram import bot
from background_task import background
from django.db.models import Q
from django.db.models import Sum

import oandapyV20.endpoints.trades as trades
from oandapyV20.endpoints.transactions import TransactionsSinceID,TransactionList,TransactionDetails

import telegram
import logging

import json
import ast
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.pricing as pricing
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from oandapyV20.contrib.requests import ClientExtensions
from oandapyV20.contrib.requests import LimitOrderRequest
from oandapyV20.contrib.requests import StopOrderRequest
from oandapyV20.contrib.requests import TakeProfitOrderRequest
from oandapyV20.endpoints.orders import OrderDetails
from oandapyV20.endpoints.trades import TradeDetails
from oandapyV20.endpoints.trades import OpenTrades
from oandapyV20.endpoints.orders import OrderList

import oandapyV20

from trades.constants import *
#---


class OandaConfig(AppConfig):
    name = 'oanda'


def loadInstrumentData():
    token="664669077a8d4ce342d4e0f7e9917d72-c0303c5cbb6a57ba12db93df848773e5"
    account="001-011-1957873-006"
    
    client = oandapyV20.API(access_token=token,environment="live")
    params = {}
    r = accounts.AccountInstruments(accountID=account, params=params)
    client.request(r)
    ins=r.response['instruments']
    #{'name': 'SGD_HKD', 'type': 'CURRENCY', 'displayName': 'SGD/HKD', 'pipLocation': -4, 'displayPrecision': 5, 'tradeUnitsPrecision': 0, 'minimumTradeSize': '1', 'maximumTrailingStopDistance': '1.00000', 'minimumTrailingStopDistance': '0.00050', 'maximumPositionSize': '0', 'maximumOrderUnits': '100000000', 'marginRate': '0.02', 'tags': [{'type': 'ASSET_CLASS', 'name': 'CURRENCY'}]}
    
    print("{},{},{},{},{}".format('name','type','pipLocation','displayPrecision','minimumTradeSize'))
    for i in ins:
        print("{},{},{},{},{}".format(i['name'],i['type'],i['pipLocation'],i['displayPrecision'],i['minimumTradeSize']))
        pf=1
        for c in range(0,abs(int(i['pipLocation']))): pf = pf * 10 
        try:
            instrument = Instrument.objects.get(name=i['name'])
        except:
            instrument = Instrument(name=i['name'],type=i['type'],pipLocation=i['pipLocation'],pipfactor=1/pf,displayPrecision=i['displayPrecision'],minimumTradeSize=i['minimumTradeSize'])
        
        instrument.type=i['type']
        instrument.pipLocation=i['pipLocation']
        instrument.pipfactor=1/pf
        instrument.displayPrecision=i['displayPrecision']
        instrument.minimumTradeSize=i['minimumTradeSize']
        instrument.save()
         

class Oanda:
#    def __init__(self,account_id, symbol, type,price,stoploss,takeprofit,risk=None,status=UNKNOWN,transaccount_id, symbol, type,price,stoploss,takeprofit,risk=None,status=UNKNOWN,transactionID=NoneactionID=None):
    def __init__(self,**kwargs):

        account_id=kwargs.get("account_id")
        symbol=kwargs.get("symbol",None)
        type=kwargs.get("type",None)
        price=kwargs.get("price",None)
        stoploss=kwargs.get("stoploss",None)
        takeprofit=kwargs.get("takeprofit",None)
        risk=kwargs.get("risk",None)
        status=kwargs.get("status",UNKNOWN)
        transactionID=kwargs.get("transactionID",None)

        self.logger = logging.getLogger(__name__)

        self.logger.debug("oanda -init: transactionID {} symbol {} account_id {} price {} ".format(transactionID,symbol,account_id,price))


        account = Account.objects.select_related("type").get(id=account_id)
        broker = Broker.objects.get(pk=account.broker_id)

        self.trade_id=0
        self.token =  account.token
        self.account = account.account_no
        self.environment=account.type.environment
        self.api = oandapyV20.API(environment=self.environment,access_token=self.token)

        if symbol == None and type==None:
            return  

        instrument = Instrument.objects.filter(symbol=symbol).first()
        if not instrument:
            instrument = Instrument.objects.filter(name=symbol).first()
            if not instrument:
                self.logger.debug("oanda error, Instrument dosent exist, {}".format(symbol))
                raise InstrumentIsNotTradeable("Instrument is not found")

        self.type = int(type)
        if self.type in [BUYLIMIT,BUYSTOP,SELLLIMIT, SELLSTOP]:
            self.pending=True
        else:
            self.pending=False
        self.status= status

        self.symbol = instrument.name 
        self.maximumTradeSize=instrument.maximumTradeSize
        self.minimumTradeSize=instrument.minimumTradeSize
        try:     
            self.price = float(price)
        except:
            pass
        try:
            self.stoploss = float(stoploss)
        except:
            self.stoploss = 0
            pass

        try:    
            self.takeprofit = float(takeprofit)
        except:
            self.takeprofit = 0
            pass

       #self.size = size
        try:
            self.risk = int(risk)
        except:
            pass
        self.pipFactor = instrument.pipFactor
        self.transactionID = transactionID

        if self.type in [ BUY,BUYLIMIT,BUYSTOP]:
            self.direction=1
        else:
            self.direction=-1
        
        if self.transactionID != None:
            self.logger.debug("transaction is given try to get update {}".format(self.transactionID))
            self.getUpdate()

    def getUpdate(self):
        self.logger.debug("getUpdate: entry status {}".format(self.status))
        if self.status == PENDING:
            return self.getOrderUpdate()
        if self.status == ACTIVE:
            return self.getTradeUpdate()
        if self.status == CLOSED:
            return self.getTradeUpdate()

    def getOrderUpdate(self):
        self.logger.debug("getOrderUpdate: entry orderid {}".format(self.transactionID,self.transactionID))
        
        r = OrderDetails(accountID=self.account, orderID=self.transactionID)
        try:
           rv = self.api.request(r)
           self.logger.debug("getOrderUpdate: trans detail{}".format(rv["order"]))
           state =  rv["order"]["state"]
           order = rv["order"]
           self.units = order["units"]
           if state == "FILLED":
                if "tradeOpenedID" in order:
                    self.trade_id=order["tradeOpenedID"]
                    self.transactionID=rv["order"]["tradeOpenedID"]
                    self.status=ACTIVE
                    self.getTradeUpdate()
                    return
                if "tradeClosedIDs" in order:
                    self.trade_id=order["tradeClosedIDs"][0]
#                    self.close_time = ""
#                    self.realizedPL = 
                    #self.transactionID=order["tradeOpenedID"]
                    self.status=CLOSED
                    return
                if "fillingTransactionID" in order:
                    transaction=order["fillingTransactionID"]
                    transdetail = self.getTransactionDetail(transaction)
                    self.logger.debug("getUpdate: order  with fillingTransactionID  getting transaction  {}".format(transdetail))
                    if "tradeReduced" in transdetail:
                        self.trade_id = transdetail["tradeReduced"]["tradeID"]
                        self.status = ACTIVE;
                        self.logger.debug("getUpdate: order opened with tradeReduced  id {} ".format(self.trade_id))
                        self.getTradeUpdate()
                        return
                                     
                self.logger.debug("getUpdate: order FILLED but status is unknown  {}".format(order))


           if state == "CANCELLED":
                self.status=CANCELED
                transaction=rv["order"]["cancellingTransactionID"]
                transdetail = self.getTransactionDetail(transaction)
                self.close_reason = transdetail["reason"]
                self.close_time = transdetail["time"]
                self.logger.debug("getUpdate: order cancled {} ".format(self.transactionID))
           self.logger.debug("getUpdate: order check if  status {} changed".format(self.status))
        except oandapyV20.exceptions.V20Error as err:
#           self.logger.debug("getUpdate: exception occered orderid {} err {}".format(self.transactionID,err))
           self.err_status_code =  r.status_code
           self.err= err
           message=ast.literal_eval(err.msg)       
           self.err_reason=message["errorMessage"]
           self.logger.debug("getUpdate: exception occered orderid {} err message {}".format(self.transactionID,self.err_reason))
           
        return

    def getTradeUpdate(self):
        self.logger.debug("getTradeUpdate: entry id {}".format(self.transactionID))
        
        r = TradeDetails(accountID=self.account, tradeID=self.transactionID)
        try:
           rv = self.api.request(r)
           tr = rv["trade"]
           if tr["state"] == "CLOSED":
                self.status=CLOSED
                self.realizedPL=tr["realizedPL"]
                self.logger.debug("getTrdeUpdate: trade closed profit {}".format(self.realizedPL))
           if tr["state"] == "OPEN":
                self.status=ACTIVE
                self.trade_id=tr["id"]
                self.logger.debug("getTrdeUpdate: trade still Active id {}".format(self.trade_id))
           self.logger.debug("getUpdate: order status {}".format(self.status))
        except oandapyV20.exceptions.V20Error as err:
#           self.logger.debug("getUpdate: exception occered orderid {} err {}".format(self.transactionID,err))
           self.err_status_code =  r.status_code
           self.err= err
           self.err_reason=str(dir(err)) 
           self.logger.debug("getUpdate: exception occered orderid {} err message {} , err {} ".format(self.transactionID,self.err_reason,err))
           raise
        return

        pass
    def chekUnitSize(self):
        if  ( self.units  > self.maximumTradeSize ): self.units = self.maximumTradeSize
        if  ( self.units  < self.minimumTradeSize ): self.units = self.minimumTradeSize

    def putTrade(self,order=None):
        self.chekUnitSize() 
        params = dict( instrument=self.symbol , units=self.units)
        if self.takeprofit != 0:  params=dict(params.items(), takeProfitOnFill=TakeProfitDetails(price=self.takeprofit).data )
        if self.stoploss != 0:  params=dict(params.items(), stopLossOnFill=StopLossDetails(price=self.stoploss).data)
        if self.pending:
            # params.update({"timeInForce": "GTC","positionFill": "INVERSE"}) 
            params=dict(params.items(),price=self.price)
            orderinfo = LimitOrderRequest(**params)
            self.logger.debug("putting limit order {}".format(orderinfo.data))
        else:
            orderinfo = MarketOrderRequest(**params)
            self.logger.debug("putting mktorder {}".format(orderinfo.data))

        #clientExtensions=ClientExtensions(clientID=str(MyOrders[order].msgid),clientComment=str(MyOrders[order].msgid)).data,
        r = orders.OrderCreate(accountID=self.account, data=orderinfo.data)
        ok=True

        try:
            rv = self.api.request(r)
            # self.logger("get rv   , status code {}".format(rv.status_code))
            self.logger.debug(json.dumps(rv, indent=2))
            if "orderCancelTransaction" in rv:
                cancelReason=rv["orderCancelTransaction"]["reason"]
                self.transactionID=rv["orderCancelTransaction"]["id"]
                self.status=FAILED
                self.err_reason=cancelReason
                ok=False
                self.logger.debug("trade open cancled with code: {}  cancelReason: {}".format(r.status_code,cancelReason))
                return(ok)
            if self.pending:
                self.transactionID=rv["orderCreateTransaction"]["id"]
                self.status=PENDING
                ok=True
                self.logger.debug("order create  id {}".format(self.transactionID))
            else:
                if self.pending:
                    self.logger.debug("pending order rv: {}".format(rv))
                    fillOrder=rv["orderFillTransaction"]["tradeOpened"]["orderID"]
                    self.status=ACTIVE
                    self.trade_id=fillOrder
                    self.transactionID=fillOrder
                    self.open_price = float(rv["orderFillTransaction"]["tradeOpened"]["price"])
                    self.open_time = rv["orderFillTransaction"]["time"] # couldn't find a better time
                    self.logger.debug("trade open trans id {} open price {} open time {}".format(self.transactionID,self.open_price,self.open_time))
                    ok=True
                else:
                    fillOrder=rv["orderFillTransaction"]["tradeOpened"]["tradeID"]
                    self.status=ACTIVE
                    self.trade_id=fillOrder
                    self.transactionID=fillOrder
                    self.open_price = float(rv["orderFillTransaction"]["tradeOpened"]["price"])
                    self.open_time = rv["orderFillTransaction"]["time"] # couldn't find a better time
                    self.logger.debug("trade open trans id {} open price {} open time {}".format(self.transactionID,self.open_price,self.open_time))
                    ok=True
        except oandapyV20.exceptions.V20Error as err:
            self.logger.debug("trade failed with code: {}  msg: {}".format(r.status_code,err))
            message=ast.literal_eval(err.msg)["orderRejectTransaction"]
            self.TransactionId=message["id"]
            self.status=FAILED
            self.err_reason=message["rejectReason"]
            ok=False
        return(ok)

    def calculate_size(self,stoploss=None,atprice=None):
        if stoploss == None: stoploss=self.stoploss
        if atprice == None: atprice=self.price

        self.currentPrice , self.qhcf = self.getPriceDetail()
        #pips = round((self.atprice - price ) / self.pipFactor)
        if not (self.stoploss == None or self.stoploss)  == 0:
            if self.pending:
                self.units=round(self.risk/(self.qhcf*abs(self.stoploss - atprice ))) * self.direction
            else:
                self.units=round(self.risk/(self.qhcf*abs(self.stoploss - self.currentPrice ))) * self.direction
        return

    def getPriceDetail(self):
        params = { "instruments" : self.symbol}
        r = pricing.PricingInfo(accountID=self.account, params=params)
        rv = self.api.request(r)
        res=rv['prices'][0]
        bid=res['bids'][0]['price']
        ask=res['asks'][0]['price']
        
        if self.direction < 0 :
            qhcf=float(res["quoteHomeConversionFactors"]['negativeUnits'])
            price=float(bid)
        else:
            qhcf=float(res["quoteHomeConversionFactors"]['positiveUnits'])
            price=float(ask)
        #ins=rv['instrument']
        #ret={"price":price,"bid": bid, "ask": ask,"QHCF":qhcf}
        return(price,qhcf)

    def closeTrade(self,half=None,units=None):
        ok=True
        if half!=None:
           units=abs(round(int(self.units)/2))
           data={ "units": str(int(units)) }
        elif units != None:
           data={ "units": str(int(units)) }
        else:
            data = None

        r = trades.TradeClose(accountID=self.account, tradeID=int(self.transactionID),data=data)
#           r = trades.TradeClose(accountID=self.account, tradeID=int(self.transactionID))
        
        try:
            rv = self.api.request(r)
            self.logger.debug("oanda.closeTrade trade, getting info from rv {}".format(rv))
            if "orderCancelTransaction" in rv:
                cancelReason=rv["orderCancelTransaction"]["reason"]
                self.err_reason=cancelReason
                ok=False
                self.logger.debug("trade close cancled with code: {}   reson {}".format(r.status_code,cancelReason))
                return(ok)

            if half!=None:
                self.closed_units=units
            else:
                if "orderFillTransaction" in rv:
                    self.close_time = rv["orderFillTransaction"]["time"]
                    self.status = CLOSED

            self.realizedPL= 0
            for item in rv["orderFillTransaction"]["tradesClosed"]:
                self.realizedPL+= float(item["realizedPL"])
                self.logger.debug("oanda.closeTrade realizedPL {}".format(self.realizedPL))

        except oandapyV20.exceptions.V20Error as err:
           self.logger.debug("oanda.closeTrade closing failed with err: {}  msg: {}".format(err, r.status_code))
           self.err_status_code =  r.status_code
           self.err= err
           raise
           ok=False
        return(ok)

    def updateTrade(self,orderid=None):
        data = {}
        ok=True
        self.logger.debug("oanda,updateTrade: entering orderid {} trs id {}".format(orderid,self.transactionID))
        if not (self.stoploss == 0  or self.stoploss == None):
                data=dict(stopLoss = dict(timeInForce= "GTC",price= str(self.stoploss)) ) 
        if not ( self.takeprofit == 0 or self.takeprofit == None):
                data=dict(data.items() , takeProfit= dict(timeInForce= "GTC", price = str(self.takeprofit)))

        self.logger.debug("sending trade update to api tradeid:{} , date: {}".format(self.transactionID,data))
        if data != {}:
            r = trades.TradeCRCDO(accountID=self.account,tradeID=self.transactionID, data=data)
            try:
            # create the OrderCreate request
                rv = self.api.request(r)
            except oandapyV20.exceptions.V20Error as err:
                self.logger.debug("Trade Modify failed {}".format(err))
                self.err_code =  r.status_code
                message=ast.literal_eval(err.msg)
                #self.status=4
                self.err_reason=message["errorMessage"]
                ok=False
        else:
            self.logger.debug("nothing to update tradeid:{} , date: {}".format(self.transactionID,data))
            ok=True
        return(ok)

    def cancelOrder(self):
        ok=True
        r = orders.OrderCancel(accountID=self.account, orderID=self.transactionID)
        try:
            rv = self.api.request(r)
            self.status=CANCELED
            self.close_reason="Signal request to close"
        except oandapyV20.exceptions.V20Error as err:
            self.logger.debug(r.status_code, err)
            for e in err:
             print("DBG cancle error, ",r.status_code , e)
            ok=False
            raise
        #else:
        #if order != 0:
        #    try:
        #        cancelReason=rv["orderCancelTransaction"]["reason"]
        #        if order != 0:
        #    MyOrders[order].comment=MyOrders[order].comment+":Trade Update,cancle reason:"+cancelReason
        return(ok)
    def replaceOrder(self):
        ok=self.cancelOrder()
        if ok: 
            self.calculate_size()
            ok=self.putTrade() 
        return(ok) 

    def getTransactionList(self,frm=None):
        trs=[]
        param={  }
        r = TransactionList(accountID=self.account,params=param)
        try:
           rv = self.api.request(r)
        except oandapyV20.exceptions.V20Error as err:
           Error("Getting transactions error:",r.status_code, err)
        self.logger.debug("getTransactionList: transactions result:{}".format(rv)) 
        tr=rv["transactions"]
        return(trs)

    def getTransactionDetail(self,id=None):
        r = TransactionDetails(accountID=self.account,transactionID=id)
        try:
           rv = self.api.request(r)
        except oandapyV20.exceptions.V20Error as err:
            ecode=json.loads(err.msg)["errorCode"]
            raise
        return(rv["transaction"])
  
    def getTransactions(self):
        trs=[]
        while True:
            param={ "id": fromID }
            r = TransactionsSinceID(account,params=param)
            try:
                rv = self.api.request(r)
            except oandapyV20.exceptions.V20Error as err:
                Error("Getting transactions error:",r.status_code, err)
    
            tr=rv["transactions"]
            trs=trs+tr
            if len(tr) == 0:
                break
            else:
                fromID=int(tr[-1]['id'])
        return(trs)
    def list_trades(self):

        r = OpenTrades(accountID=self.account)
        try:
            rv = self.api.request(r)
            self.logger.debug("list_trades: status code {} ".format(r.status_code)) 
            tradelist=rv["trades"]
            return(tradelist)
        except oandapyV20.exceptions.V20Error as err:
            self.logger.debug("list_trades: exceptions to get trade list, code: {} msg: {} , dir r {} , dict  r {}".format(r.status_code, err,dir(r),r.__dict__)) 
        

    
    def list_order(self):
        r = trades.OrderList(accountID=self.account)
        try:
            rv = self.api.request(r)
            return(rv["orders"])
        except oandapyV20.exceptions.V20Error as err:
            self.logger.debug("list_orders: exceptions to get orders list, {} {}".format(r.status_code, err)) 






class Oanda_base:
#    def __init__(self,account_id, symbol, type,price,stoploss,takeprofit,risk=None,status=UNKNOWN,transaccount_id, symbol, type,price,stoploss,takeprofit,risk=None,status=UNKNOWN,transactionID=NoneactionID=None):
    def __init__(self,**kwargs):

        import time
        millis = int(round(time.time() * 1000))
        self.millis=millis

        account_id=kwargs.get("account_id")
        self.logger = logging.getLogger(__name__)
        self.logger.debug("oanda base account {} , {} -init: ".format(self.millis,account_id))
        account = Account.objects.select_related("type").get(id=account_id)
        broker = Broker.objects.get(pk=account.broker_id)
        self.token =  account.token
        self.account = account.account_no
        self.environment=account.type.environment
        self.api = oandapyV20.API(environment=self.environment,access_token=self.token)



    def get_price_update(self):

        params = {}

        instruments = Instrument.objects.all().values('name')
        symbol_list=[]
        
        for instrument in instruments:
            symbol_list.append(instrument['name'])

        symbols=",".join(symbol_list)
        # symbols="EUR_USD,NAS100_USD"

        params = { "instruments" : symbols}

        #print(getPriceDetail(account,token,params))

        r = pricing.PricingStream(accountID=self.account, params=params)
        rv = self.api.request(r)

        
        t=0
        for ticks in rv:
          if ticks["type"] == "PRICE":
            self.logger.debug("price update for millis :{}".format(self.millis))          
            data=dict(instrument=ticks["instrument"],time=ticks["time"],bids=ticks["bids"][0]["price"], asks=ticks["asks"][0]["price"],closeoutBid=ticks["closeoutBid"],closeoutAsk=ticks["closeoutAsk"])
            # self.logger.debug("price update got:{}".format(data))          
            instrument = Instrument.objects.get(name=data["instrument"])
            instrument.tick_time=data["time"]
            instrument.bids=data["bids"]
            instrument.asks=data["asks"]
            instrument.closeoutBid=data["closeoutBid"]
            instrument.closeoutAsk=data["closeoutAsk"]
            instrument.save()        
            # check_pending_orders(symbol=data["instrument"])
