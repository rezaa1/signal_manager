from django.db import models
from signals.models import Channel
from django.db.models import DateTimeField

from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.db.models import CharField
from django.db.models import DateTimeField
from django_extensions.db.fields import AutoSlugField
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import IntegerField
from django.db.models import TextField
from django.db.models import ForeignKey
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from django.db import models as models
from django_extensions.db import fields as extension_fields

#CANCLED = 'Cancled'
#PENDING = 'Pending'
#CLOSED = 'Closed'
#ACTIVE = 'Active'
#DELETED = 'Deleted'
#

from trades.constants import *



class Trade(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    orderid = models.TextField()
    symbol = models.TextField()
#    ordeDIRECTIONpALL ordeDIRECTIONpSHORT,ordeDIRECTIONpLONG choices=0,2RDER_TYPE, max_length=10)
    type = models.CharField(max_length=10)

    stoploss = models.TextField()
    price = models.TextField()
    units = models.TextField()
    takeprofit = models.TextField()
    status = models.IntegerField(default=UNKNOWN,choices=ORDER_STATUS_CHOICES)
    open_price = models.TextField(blank=True)
    open_time = models.DateTimeField(null=True,blank=True)
    error_code = models.TextField(blank=True)
    error_reason = models.TextField(blank=True)
    close_price = models.TextField(blank=True)
    close_reason = models.TextField(blank=True)
    close_time = models.DateTimeField(null=True,blank=True)
    realizedPL = models.TextField(blank=True)
    account = models.ForeignKey('Account',on_delete=models.CASCADE)
    signal = models.ForeignKey('signals.signal',on_delete=models.CASCADE)
    order_comment = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey(
        'auth.User', related_name='trades', on_delete=models.CASCADE)
    class Meta:
        ordering = ('created', )
        unique_together = ('owner','account','orderid')
        constraints = [
            models.CheckConstraint(check=~models.Q(orderid='0'),name='orderidne0'),
        ]

    def __str__(self):
        return self.orderid + "_" + self.symbol

class Broker(models.Model):
    name = models.CharField(max_length=20,unique=True)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

class Strategy(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    stoploss = models.BooleanField(default=True)
    needsl = models.BooleanField(default=True)
    manage_trade = models.BooleanField(default=False)
    pending_order = models.BooleanField(default=True)
    break_even = models.IntegerField(blank=True)  
    close_half = models.IntegerField(blank=True)  
    size_multiplier  = models.FloatField(blank=True,default=1)  
    size_type  = models.IntegerField(blank=True,choices=STG_SIZE_TYPE,default=STG_SIZE_STOPLOSS)

    units  = models.IntegerField(blank=True,default=0) # When set, it will force the order size
    filter_enabled  = models.BooleanField(default=False) # enable filters
    filter_lot_size = models.TextField(blank=True) # filter based on lot size
    filter_direction = models.IntegerField(blank=True,choices=STG_DIRECTION,default=STG_DIRECTION_ALL)
    filter_ea_number = models.TextField(blank=True) # filter based on ea number


    #risk  = models.IntegerField(blank=True)
    
    def get_absolute_url(self):
        return reverse('trades_strategy_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('trades_strategy_update', args=(self.pk,))

    class Meta:
        ordering = ('name', )

    def get_fields(self):
        return [(field.verbose_name, field.value_from_object(self)) for field in self.__class__._meta.fields]
    
    def __str__(self):
        return self.name

class AccountType(models.Model):
    name = models.CharField(max_length=20)
    broker = models.ForeignKey('Broker',on_delete=models.CASCADE)
    environment = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name', )
        unique_together = ('broker','name')

    def __str__(self):
        return self.name

# class Account(models.Model):

#     # Fields
#     created = DateTimeField(auto_now_add=True)
#     account_no = CharField(max_length=20)
#     description = TextField(blank=True)

#     # Relationship Fields
#     type = ForeignKey(
#         'trades.AccountType',
#         on_delete=models.CASCADE, related_name="AccountType"
#     )
#     broker = ForeignKey(
#         'trades.Broker',
#         on_delete=models.CASCADE, related_name="Broker"
#     )
#     owner = ForeignKey(
#         'auth.User',
#         on_delete=models.CASCADE, related_name='accounts'
#     )

#     class Meta:
#         ordering = ('-created',)

#     def __unicode__(self):
#         return u'%s' % self.pk

#     def get_absolute_url(self):
#         return reverse('trades_account_detail', args=(self.pk,))


#     def get_update_url(self):
#         return reverse('trades_account_update', args=(self.pk,))




class Account(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    account_no = models.CharField(max_length=20)
    token  = models.CharField(max_length=100)
    type = models.ForeignKey('AccountType',on_delete=models.CASCADE)
    broker = models.ForeignKey('Broker',on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        'auth.User', related_name='accounts', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
        unique_together = ('broker','owner','account_no')

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('trades_account_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('trades_account_update', args=(self.pk,))

    def __str__(self):
        return str(self.id)+":"+self.description



class Follower(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey('Account',on_delete=models.CASCADE)
    channel = models.ForeignKey('signals.Channel',on_delete=models.CASCADE)
    strategy = models.ForeignKey('Strategy',on_delete=models.CASCADE)
    risk = models.IntegerField(default=1)
    owner = models.ForeignKey(
        'auth.User', related_name='followers', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
        unique_together = ('owner','account','channel')


    def __str__(self):
        return str(self.account )

    def get_absolute_url(self):
        return reverse('trades_follower_detail', args=(self.pk,))

    def get_update_url(self):
        return reverse('trades_follower_update', args=(self.pk,))


#class Symbol(models.Model):
#    name = models.CharField(max_length=20)
#    type = models.CharField(max_length=20)
#    pip  = models.IntegerField()
#    quoteFactor = models.FloatField()
#    broker = models.ForeignKey('Broker',on_delete=models.CASCADE)
#    accounttype = models.ForeignKey('AccountType',on_delete=models.CASCADE)
#
#    class Meta:
#        ordering = ('created', )
#        unique_together = ('name','broker','accounttype')
#


