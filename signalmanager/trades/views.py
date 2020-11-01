from django.shortcuts import render
from trades.models import  Trade,Strategy,Follower
from signals.models import  Signal as Signal
# Create your views here.

  


from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest_framework import filters
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status

from trades.serializers import *




class StrategyViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly )

class BrokerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer


class AccountTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly )


class FollowerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly )


class AccountViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly )


from django.core import serializers

#_________________________ Auto build

from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import Trade, Broker, Strategy, AccountType, Account, Follower
from .forms import TradeForm, BrokerForm, StrategyForm, AccountTypeForm, AccountForm, FollowerForm

from django.shortcuts import redirect
from django.conf import settings

class SignalListView(ListView):
    
    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, self.request.path))
        return super().dispatch(request, *args, **kwargs)


    
class SignalCreateView(CreateView):
    
    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, self.request.path))
        return super().dispatch(request, *args, **kwargs)


class SignalDetailView(DetailView):
    
    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, self.request.path))
        return super().dispatch(request, *args, **kwargs)

class SignalUpdateView(UpdateView):
    
    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, self.request.path))
        return super().dispatch(request, *args, **kwargs)


class TradeListView(SignalListView):
    model = Trade


class TradeCreateView(SignalCreateView):
    model = Trade
    form_class = TradeForm
    # if not request.user.is_authenticated:
    #     redirect('%s?next=%s' % ('/login/', request.path))
 

class TradeDetailView(SignalDetailView):
    model = Trade


class TradeUpdateView(SignalUpdateView):
    model = Trade
    form_class = TradeForm


class BrokerListView(SignalListView):
    model = Broker


class BrokerCreateView(SignalCreateView):
    model = Broker
    form_class = BrokerForm


class BrokerDetailView(SignalDetailView):
    model = Broker


class BrokerUpdateView(SignalUpdateView):
    model = Broker
    form_class = BrokerForm


class StrategyListView(SignalListView):
    model = Strategy
#    data = serializers.serialize( "python", Strategy.objects.all() )


class StrategyCreateView(SignalCreateView):
    model = Strategy
    form_class = StrategyForm


class StrategyDetailView(SignalDetailView):
    model = Strategy


class StrategyUpdateView(SignalUpdateView):
    model = Strategy
    form_class = StrategyForm


class AccountTypeListView(SignalListView):
    model = AccountType


class AccountTypeCreateView(SignalCreateView):
    model = AccountType
    form_class = AccountTypeForm


class AccountTypeDetailView(SignalDetailView):
    model = AccountType


class AccountTypeUpdateView(SignalUpdateView):
    model = AccountType
    form_class = AccountTypeForm


class AccountListView(SignalListView):
    model = Account


class AccountCreateView(SignalCreateView):
    model = Account
    form_class = AccountForm


class AccountDetailView(SignalDetailView):
    model = Account


class AccountUpdateView(SignalUpdateView):
    model = Account
    form_class = AccountForm


class FollowerListView(SignalListView):
    model = Follower


class FollowerCreateView(SignalCreateView):
    model = Follower
    form_class = FollowerForm


class FollowerDetailView(SignalDetailView):
    model = Follower


class FollowerUpdateView(SignalUpdateView):
    model = Follower
    form_class = FollowerForm
