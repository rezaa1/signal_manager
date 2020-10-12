from trades.error import *

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

from oanda.apps import Oanda,Oanda_base
import oandapyV20

from trades.constants import *

print("DBG_trade1")
logger = logging.getLogger(__name__)
print("DBG_trade2")



class TradesConfig(AppConfig):
    name = 'trades'

@background(queue='trade-mnt',schedule=5)
def maintain_trades():
    '''
     look for active trades , and thier signals 
     if signal is closed and trade is not, close the trade.

    '''
    
    logger.debug("Entring trade maintenace - check active trades on db")
    
    trades= Trade.objects.select_related("signal").filter(Q(signal__order_status__in=['Cancled','Closed'])).filter(Q(status__in=[0,1]))
    for trade in trades:
        logger.debug("maintenace - Found trade to close {}:{}".format(trade.id,trade.symbol))
        close_order(trade)

    logger.debug("Entring trade maintenace - check active trade in accounts")
    accounts = Account.objects.select_related("type").all()
    #broker = Broker.objects.get(pk=account.broker_id)
    for account in accounts:
        logger.debug("check active trade in account {}".format(account.account_no))
        maintain_account(account.id)



@background(queue='trade-mnt')
def maintain_account(aid):

    account = Account.objects.select_related("type").get(pk=aid)
    oanda = Oanda(account_id=account.id)
    try:
        trade_list = oanda.list_trades()
        tr_ids=[]
        for tr in trade_list:
            tr_ids.append(tr["id"])

        logger.debug("Active trade in account {} , {} ".format(account.account_no,len(trade_list)))

        trades= Trade.objects.select_related("signal").filter(Q(signal__order_status__in=['Cancled','Closed'])).filter(Q(orderid__in=tr_ids))
        

        for trade in trades:
            logger.debug("Active trade {}, {} in account {} found which should be closed ".format(trade.orderid,trade.symbol,account.account_no))
            try:
                close_order(trade,force=True)
            except:
                pass
                 

    except:
        logger.debug("check active trade - error  {}".format(account.account_no))
        pass




@background(queue='trade-queue')
def manage_trades(signal_id,update=None):

    # from channel of signal, find follwoers
    # get accounts
    # compare exisitng trades
    # if not find, action create
    # else find changes,, action modify
    logger.debug("------------------------ Entring trade manage sigid {}, update: {}".format(signal_id,update ))

    signal = Signal.objects.get(pk=signal_id)
    signal.owner
    signal.channel_type_free

    followers = Follower.objects.select_related("channel").select_related("account").filter(Q(channel__type=signal.channel_type_free)|Q(channel__type=signal.channel_type_paid),owner=signal.owner)

    for follower in followers:
        logger.debug("follower account {} ".format(follower.account) )
        stg = Strategy.objects.get(pk=follower.strategy_id)
        trade=None
        try:
            trade = Trade.objects.get(account = follower.account, owner= signal.owner, signal=signal)
        except:
            pass
        if trade == None:
            if signal.order_status not in ['Closed','Cancled','Deleted']:
                create_order(signal,follower)
        else:
            if update == None:
                logger.debug("STRANGE! no update for this {} {} {}".format(signal_id,signal.order_status,signal.order_symbol))
                return
                

            if 'stoploss' in update or 'takeproffit' in update:
                update_order(signal,follower,trade,update)
            if 'status' in update and  signal.order_status  in ["Closed","Cancled","Deleted"]:
                close_order(signal=signal,follower=follower,trade=trade)
#            res.update(price=request['order_price'])
#            res.update(status=request['order_status'] )
#            res.update(type=request['order_type'] )
#            res.update(lot=request['order_lot'])


def create_order(signal,follower,trade=None):

    logger.debug("trade entry account no {} signal {} trade {} ".format(follower.account.account_no,signal.id,trade) )
    stg = Strategy.objects.get(pk=follower.strategy_id)
    risk = follower.risk
    
    if trade == None:
        # Strategey Check Start
        if stg.filter_enabled:
            if stg.filter_lot_size is not None:
                if signal.order_lot != stg.filter_lot_size: 
                    logger.debug("signal {} symbol {} , lot size {} , ignoring as of strategy filter_lot_size".format(signal.id,signal.order_symbol,signal.order_lot) ) 
                    return

            if stg.filter_direction is not STG_DIRECTION_ALL:
                if stg.filter_direction == STG_DIRECTION_LONG:                                    
                    if int(signal.order_type) not in [BUYLIMIT,BUYSTOP,BUY]: 
                        logger.debug("signal {} symbol {} ,  type {} , ignoring as of strategy filter_direction no BUY".format(signal.id,signal.order_symbol,signal.order_type) ) 
                        return
                if stg.filter_direction == STG_DIRECTION_SHORT:                                    
                    if int(signal.order_type) not in [SELLLIMIT,SELLSTOP,SELL]: 
                        logger.debug("signal {} symbol {} ,  type {} , ignoring as of strategy filter_direction no SELL ".format(signal.id,signal.order_symbol,signal.order_type) ) 
                        return


        if ( signal.order_stoploss == '0' or signal.order_stoploss == "" or signal.order_stoploss == None ) and stg.needsl == True:
            logger.debug("signal {} symbol {} , no stoploss , ignoring".format(signal.id,signal.order_symbol) )
            return  
        if stg.pending_order == False and signal.order_status ==  "Pending":
            logger.debug("signal {} symbol {} is pending order. ignoring as of strategy".format(signal.id,signal.order_symbol) )
            return  
        accid=follower.account.id
        logger.debug("account id {} ".format(accid) )
        
        try:
            oanda = Oanda(account_id=accid,symbol=signal.order_symbol, price=signal.order_price,stoploss=signal.order_stoploss, takeprofit=signal.order_takeprofit,risk=follower.risk,type=signal.order_type,status=signal.order_status)
        except InstrumentIsNotTradeable as e:
            logger.error("Oanda error, signal {} , account {} ,symbol {} , error: {}".format(signal.id, accid, signal.order_symbol,e))
            return

        if stg.size_type == STG_SIZE_MULTIPLIER:
            logger.debug(" stg is STG_SIZE_MULTIPLIER , :{} :{}: {} ".format(signal.order_lot ,LOTS_UNITS , stg.size_multiplier) )
            signal_units = float(signal.order_lot) * LOTS_UNITS
            trade_units =  round( signal_units * float(stg.size_multiplier))
            oanda.units = trade_units * oanda.direction
        elif stg.size_type == STG_SIZE_FIX:
            oanda.units = stg.units * oanda.direction
            logger.debug(" stg is STG_SIZE_FIX , :order lot {} multiplier in stg:{} , units:{} ".format(signal.order_lot  , stg.size_multiplier,oanda.units) )
        elif stg.size_type == STG_SIZE_RISK:
            oanda.calculate_size()
            logger.debug(" stg is STG_SIZE_RISK , :order lot {} , units:{} ".format(signal.order_lot  , oanda.units) )

        if stg.stoploss == False: 
            logger.debug(" stg is stoposs false , set stop loss to 0  signal {}".format(signal.id) )
            oanda.stoploss = 0
        # Strategey Check END
        
        ok=oanda.putTrade()
        trade = Trade(account_id = accid, owner= signal.owner, signal=signal, price=oanda.price,stoploss=oanda.stoploss, takeprofit=oanda.takeprofit,type=oanda.type,symbol=oanda.symbol)
        if ok:
            if oanda.pending:
                trade.orderid=oanda.transactionID
                trade.status=oanda.status
                logger.debug(" put pending order ok id {} sttus {}".format(trade.orderid,trade.status ))
            else: 
                trade.status=oanda.status
                trade.open_price=oanda.open_price
                trade.open_time=oanda.open_time
                trade.orderid=oanda.trade_id
                logger.debug(" put market order ok id {} sttus {}".format(trade.orderid,trade.status ))
            
            trade.units = oanda.units

        else:
#            trade.error_code=oanda.err_code
            trade.orderid=oanda.transactionID
            trade.error_reason=oanda.err_reason
        trade.save()

def close_order(trade,signal=None,follower=None,force=False):
    logger.debug("close_order: trade {} symbol {} ".format(trade.orderid,trade.symbol) )
#    stg = Strategy.objects.get(pk=follower.strategy_id)
    
    #accid=follower.account.id
    accid=trade.account.id
    if trade.status in [CLOSED,CANCELED]:
        if force:
            logger.debug("close_order:  trade {} {} already closed, synce forced continue ".format(trade.orderid,trade.symbol) )
        else:
            logger.debug("close_order:  trade {} {} already closed, ignoring ".format(trade.orderid,trade.symbol) )
            return 

#    oanda = Oanda(account_id=accid,symbol=signal.order_symbol, price=signal.order_price,stoploss=signal.order_stoploss, takeprofit=signal.order_takeprofit,risk=follower.risk,type=signal.order_type,transactionID=trade.orderid,status=trade.status)
    oanda = Oanda(account_id=accid,symbol=trade.symbol, price=trade.price,stoploss=trade.stoploss, takeprofit=trade.takeprofit,transactionID=trade.orderid,status=trade.status,type=trade.type)
    ok=False
    if oanda.status == PENDING:
        ok=oanda.cancelOrder()
    if oanda.status == ACTIVE: 
            ok=oanda.closeTrade()
    trade.status=oanda.status
    if oanda.status == CLOSED:
        trade.status = oanda.status
        try:
            trade.realizedPL = oanda.realizedPL
        except:
            logger.warning("close_order: account{} signal {} trade {} no oanda.realizedPL ".format(accid,trade.signal_id,trade.orderid) )
            pass
        try:
            trade.close_time=oanda.close_time
        except:
            logger.warning("close_order: account{} signal {} trade {} no oanda.close_time ".format(accid,trade.signal_id,trade.orderid) )
            pass
    
        ok=True
    if oanda.status == CANCELED:
        try:
            trade.close_reason=oanda.close_reason
        except:
            pass
        try:    
            trade.close_time=oanda.close_time
        except:
            pass


        ok=True
    if ok:
        logger.debug("dbg point {}".format(6) )
        trade.save()
    else:
        logger.debug("not ok passed, so what {} , {} ".format(oanda,oanda.__dict__))



def update_order(signal,follower,trade,update):
    logger.debug("update_order entry account no {} signal {} trade {} update {} ".format(follower.account.account_no,signal.id,trade,update) )
    stg = Strategy.objects.get(pk=follower.strategy_id)
    
    accid=follower.account.id
    if trade.status == CLOSED or trade.status == CANCELED:
        logger.debug("update_order trade/order {} marked as {} ignoring this update {}".format(signal.id,trade.status,update) )
        return
        
    oanda = Oanda(account_id=accid,symbol=signal.order_symbol, price=signal.order_price,stoploss=signal.order_stoploss, takeprofit=signal.order_takeprofit,risk=follower.risk,type=signal.order_type,status=trade.status,transactionID=trade.orderid)
    trade.status=oanda.status
    if stg.stoploss == False: 
       oanda.stoploss = 0
    if oanda.status == PENDING:
        logger.debug("update_order status pending {} replacing order".format(oanda.status) )
        ok=oanda.replaceOrder()
        if ok:
            if oanda.pending:
                trade.orderid=oanda.transactionID
                trade.status=oanda.status
                logger.debug(" put order ok id {} sttus {}".format(trade.orderid,trade.status ))
            else: 
                trade.status=oanda.status
                trade.open_price=oanda.open_price
                trade.open_time=oanda.open_time
                trade.orderid=oanda.trade_id
            trade.units = oanda.units
        else:
#            trade.error_code=oanda.err_code
            trade.orderid=oanda.transactionID
            trade.error_reason=oanda.err_reason
        trade.save()

        return(ok)







    if oanda.status == ACTIVE:
        logger.debug("update_order status active {} updateing trade".format(oanda.status) )
        ok=oanda.updateTrade()
        trade.orderid=oanda.trade_id
        if ok:
            logger.debug("update_order status active {} updateing db".format(oanda.status) )
            trade.stoploss=oanda.stoploss
            trade.takeprofit=oanda.takeprofit
            trade.price=oanda.price
   #         trade.orderid=oanda.trade_id
            trade.save()
        return(ok)

    if oanda.status == CLOSED:
        trade.status = oanda.status
        trade.realizedPL = oanda.realizedPL
        trade.save()
        return

    if oanda.status == CANCELED:
        trade.close_reason=oanda.close_reason
        trade.close_time=oanda.close_time
        trade.save()
        return

      

      

@background(queue='price-update-queue')
def maintain_price_update():

    oanda = Oanda_base(account_id=5)
    oanda.get_price_update()

# def check_pending_orders(data):

    # signal = Signal.objects.get(order_status='Pending')
