from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


#LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
#ORDER_TYPE = sorted ( ["buy" , "sell" , "sellstop" , "buystop" , "selllimit" , "buylimit"  ] )


# OP_BUY 0 Buy operation
# OP_SELL 1 Sell operation
# OP_BUYLIMIT 2 Buy limit pending order
# OP_SELLLIMIT 3 Sell limit pending order
# OP_BUYSTOP 4 Buy stop pending order
# OP_SELLSTOP 5 Sell stop pending order
 


CANCLED = 'Cancled'
PENDING = 'Pending'
CLOSED = 'Closed'
ACTIVE = 'Active'
DELETED = 'Deleted'

ORDER_STATUS_CHOICES = (
        (CANCLED, 'Cancled'),
        (PENDING, 'Pending'),
        (CLOSED, 'Closed'),
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
    )
 
CHANNEL_TYPE_CHOICES = [ (0,'Free'),(1,'Paid')]
 

class Signal(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_id = models.TextField()
    order_symbol = models.TextField()
#    order_type = models.CharField(choices=ORDER_TYPE, max_length=10)
    standard_symbol = models.TextField(blank=True,null=True)
    order_type = models.CharField(max_length=10)
    order_stoploss = models.TextField(max_length=20,blank=True,null=True)
    order_price = models.TextField()
    order_lot = models.TextField()
    order_create_time = models.CharField(max_length=20,blank=True,null=True)
    order_open_time = models.CharField(max_length=20,blank=True,null=True)
    order_close_time = models.CharField(max_length=20,blank=True,null=True)
    order_close_price = models.CharField(max_length=20,blank=True,null=True)
    order_takeprofit = models.TextField(max_length=20,blank=True,null=True)
    order_status = models.CharField(default='',max_length=10,choices=ORDER_STATUS_CHOICES)
    message_id = models.TextField(default='0')
    order_comment = models.CharField(max_length=100, blank=True, default='')
    strategy = models.CharField(max_length=100, blank=True, default='')

    channel_type_free = models.CharField(default='FREE',max_length=10,choices=CHANNEL_TYPE_CHOICES )
    channel_type_paid = models.CharField(default='',max_length=10,choices=CHANNEL_TYPE_CHOICES)

    owner = models.ForeignKey(
        'auth.User', related_name='signals', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
        unique_together = (('order_id'),'owner')


    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code signal.
        """

        super(Signal, self).save(*args, **kwargs)


class Channel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    channel_id = models.TextField(unique=True)
    title = models.TextField()
    type = models.CharField(default='',max_length=10,choices=CHANNEL_TYPE_CHOICES )
    owner = models.ForeignKey(
        'auth.User', related_name='channels', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
#        unique_together = ('tcid')


    def __str__(self):
        return self.title


'''
ACCOUNT_LOGIN
Account number
ACCOUNT_TRADE_MODE
Account trade mode
ENUM_ACCOUNT_TRADE_MODE
ACCOUNT_LEVERAGE
ACCOUNT_BALANCE
ACCOUNT_CREDIT
ACCOUNT_PROFIT
ACCOUNT_EQUITY
ACCOUNT_MARGIN
ACCOUNT_MARGIN_FREE
ACCOUNT_MARGIN_LEVEL
ACCOUNT_MARGIN_SO_CALL
ACCOUNT_MARGIN_SO_SO
ACCOUNT_MARGIN_INITIAL
ACCOUNT_MARGIN_MAINTENANCE
ACCOUNT_ASSETS
ACCOUNT_LIABILITIES
ACCOUNT_COMMISSION_BLOCKED
ACCOUNT_NAME
ACCOUNT_SERVER
ACCOUNT_CURRENCY
ACCOUNT_COMPANY
ACCOUNT_TRADE_MODE_DEMO
ACCOUNT_TRADE_MODE_REAL
'''
class Account(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    login = models.TextField(blank=True,null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)
    creadit = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    name = models.TextField(blank=True,null=True)
    server = models.TextField(blank=True,null=True)
    company = models.TextField(blank=True,null=True)
    updated = models.DateTimeField(auto_now=True)


    owner = models.ForeignKey(
        'auth.User', related_name='signalaccounts', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )

    def __str__(self):
        return self.name
#        unique_together = ('tcid')


class Bot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    bot_id = models.TextField()
    token = models.TextField()
    username = models.TextField()
    name = models.TextField()
    owner = models.ForeignKey(
        'auth.User', related_name='bots', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
#        unique_together = ('tcid')




class MessageRecord(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message_id = models.TextField()
    signal = models.ForeignKey(
        'Signal', related_name='messagerecords_signal', on_delete=models.CASCADE)
    channel = models.ForeignKey(
        'Channel', related_name='messagerecords_channel', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        'auth.User', related_name='messagerecords_bot', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created', )
        unique_together = (('channel'),'signal')



# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

