from django.db import models

# Create your models here.
class Instrument(models.Model):
#name,type,pipLocation,displayPrecision,minimumTradeSize

    name = models.CharField(max_length=20,unique=True)
    symbol = models.CharField(max_length=20,unique=True)
    type = models.CharField(max_length=20)
    pipLocation  = models.IntegerField()
    displayPrecision  = models.IntegerField()
    minimumTradeSize  = models.FloatField()
    pipFactor  = models.FloatField()

    tick_time = models.DateTimeField(blank=True,null=True)
    bids = models.FloatField(blank=True,null=True)
    asks = models.FloatField(blank=True,null=True)
    closeoutBid = models.FloatField(blank=True,null=True)
    closeoutAsk = models.FloatField(blank=True,null=True)


    class Meta:
        ordering = ('name', )



