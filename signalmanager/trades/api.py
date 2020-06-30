##_____ auto build
from . import models
from . import serializers
from rest_framework import viewsets, permissions


class TradeViewSet(viewsets.ModelViewSet):
    """ViewSet for the Trade class"""

    queryset = models.Trade.objects.all()
    serializer_class = serializers.TradeSerializer
    permission_classes = [permissions.IsAuthenticated]


class BrokerViewSet(viewsets.ModelViewSet):
    """ViewSet for the Broker class"""

    queryset = models.Broker.objects.all()
    serializer_class = serializers.BrokerSerializer
    permission_classes = [permissions.IsAuthenticated]


class StrategyViewSet(viewsets.ModelViewSet):
    """ViewSet for the Strategy class"""

    queryset = models.Strategy.objects.all()
    serializer_class = serializers.StrategySerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the AccountType class"""

    queryset = models.AccountType.objects.all()
    serializer_class = serializers.AccountTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for the Account class"""

    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    permission_classes = [permissions.IsAuthenticated]


class FollowerViewSet(viewsets.ModelViewSet):
    """ViewSet for the Follower class"""

    queryset = models.Follower.objects.all()
    serializer_class = serializers.FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]

