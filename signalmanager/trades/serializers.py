from django.contrib.auth.models import User
from rest_framework import serializers

from trades.models import *


class StrategySerializer(serializers.HyperlinkedModelSerializer):


    class Meta:
        model = Strategy
#        fields = ('url', 'order_id', 'order_type', 'owner', 'order_symbol', 'order_stoploss', 'order_takeprofit', 'order_price' , 'order_lot')
        fields = ('id', 'name' , 'description', 'stoploss', 'manage_trade', 'pending_order', 'break_even', 'close_half', 'size_multiplier', 'size_type', 'units', 'filter_enabled', 'filter_lot_size', 'filter_direction', 'filter_ea_number')
#        fields = ( 'id', 'order_id', 'order_type', 'owner' )



class BrokerSerializer(serializers.HyperlinkedModelSerializer):


    class Meta:
        model = Broker
        fields = '__all__' 

    

class AccountTypeSerializer(serializers.HyperlinkedModelSerializer):

    broker = BrokerSerializer()
    class Meta:
        model = AccountType
        fields = '__all__' 

    

class AccountSerializer(serializers.HyperlinkedModelSerializer):


    type = AccountTypeSerializer()

    class Meta:
        model = Account
        fields = ('account_no', 'token','description','type') 

      #     type = models.ForeignKey('AccountType',on_delete=models.CASCADE)
            # broker = models.ForeignKey('Broker',on_delete=models.CASCADE)
   

class FollowerSerializer(serializers.HyperlinkedModelSerializer):

    #account = AccountSerializer()
    class Meta:
        model = Follower
        fields = ('id','risk','account_id','strategy_id','channel_id')




#______________ auto build

from . import models

from rest_framework import serializers


class TradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Trade
        fields = (
            'pk', 
            'created', 
            'orderid', 
            'symbol', 
            'type', 
            'stoploss', 
            'price', 
            'units', 
            'takeprofit', 
            'status', 
            'open_price', 
            'open_time', 
            'error_code', 
            'error_reason', 
            'close_price', 
            'close_reason', 
            'close_time', 
            'realizedPL', 
            'order_comment', 
        )


class BrokerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Broker
        fields = (
            'pk', 
            'name', 
            'description', 
        )


class StrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Strategy
        fields = (
            'pk', 
            'name', 
            'description', 
            'stoploss', 
            'manage_trade', 
            'pending_order', 
            'break_even', 
            'close_half', 
            'filter_direction', 
            'filter_ea_number', 
        )


class AccountTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AccountType
        fields = (
            'pk', 
            'name', 
            'environment', 
            'description', 
        )


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Account
        fields = (
            'pk', 
            'created', 
            'account_no', 
            'description', 
        )


class FollowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Follower
        fields = (
            'pk', 
            'created', 
            'risk', 
        )

