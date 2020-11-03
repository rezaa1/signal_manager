from django.contrib.auth.models import User
from rest_framework import serializers

from signals.models import Signal


class SignalSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    order_open_time=serializers.CharField(required=False)
    order_close_time=serializers.CharField(required=False)
    order_create_time=serializers.CharField(required=False)

#    highlight = serializers.HyperlinkedIdentityField(
#        view_name='signal-highlight', format='html')

    class Meta:
        model = Signal
#        fields = ('url', 'order_id', 'order_type', 'owner', 'order_symbol', 'order_stoploss', 'order_takeprofit', 'order_price' , 'order_lot')
        fields = ('id', 'order_id', 'order_type', 'owner', 'order_symbol', 'order_stoploss', 'order_takeprofit', 'order_price' , 'order_lot','order_status','message_id','order_create_time','order_open_time','order_close_time','order_comment','standard_symbol')
#        fields = ( 'id', 'order_id', 'order_type', 'owner' )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    signals = serializers.HyperlinkedRelatedField(
        many=True, view_name='signal-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'signals')


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Signal
        fields = ('login', 'balance', 'creadit', 'profit', 'name', 'server', 'company', 'owner' )
