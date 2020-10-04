from django.db import models

# Create your models here.

class Map(models.Model):

    name = models.CharField(max_length=20,unique=True)
    symbol = models.CharField(max_length=20,unique=True)

    class Meta:
        ordering = ('name', )

