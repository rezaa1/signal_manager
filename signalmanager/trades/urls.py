from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from trades import views
from django.urls import path

from trades import forms

from rest_framework.authtoken.views import ObtainAuthToken
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'strategy', views.StrategyViewSet)
router.register(r'follower', views.FollowerViewSet)
router.register(r'account', views.AccountViewSet)
router.register(r'accounttype', views.AccountTypeViewSet)
router.register(r'broker', views.BrokerViewSet)
#router.register(r'followerform',forms.manage_follower,base_name='Follower')
# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]

urlpatterns += [
    path('followerform/', forms.manage_follower),
    path('accountform/', forms.manage_account),
]

# urlpatterns += [
#     url(r'^followerform', forms.manage_follower)
# ]



####________auto build


from django.urls import path, include
from rest_framework import routers

from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'trade', api.TradeViewSet)
router.register(r'broker', api.BrokerViewSet)
router.register(r'strategy', api.StrategyViewSet)
router.register(r'accounttype', api.AccountTypeViewSet)
router.register(r'account', api.AccountViewSet)
router.register(r'follower', api.FollowerViewSet)


urlpatterns += (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Trade
    path('trades/trade/', views.TradeListView.as_view(), name='trades_trade_list'),
    path('trades/trade/create/', views.TradeCreateView.as_view(), name='trades_trade_create'),
    path('trades/trade/detail/<int:pk>/', views.TradeDetailView.as_view(), name='trades_trade_detail'),
    path('trades/trade/update/<int:pk>/', views.TradeUpdateView.as_view(), name='trades_trade_update'),
)

urlpatterns += (
    # urls for Broker
    path('trades/broker/', views.BrokerListView.as_view(), name='trades_broker_list'),
    path('trades/broker/create/', views.BrokerCreateView.as_view(), name='trades_broker_create'),
    path('trades/broker/detail/<int:pk>/', views.BrokerDetailView.as_view(), name='trades_broker_detail'),
    path('trades/broker/update/<int:pk>/', views.BrokerUpdateView.as_view(), name='trades_broker_update'),
)

urlpatterns += (
    # urls for Strategy
    path('trades/strategy/', views.StrategyListView.as_view(), name='trades_strategy_list'),
    path('trades/strategy/create/', views.StrategyCreateView.as_view(), name='trades_strategy_create'),
    path('trades/strategy/detail/<int:pk>/', views.StrategyDetailView.as_view(), name='trades_strategy_detail'),
    path('trades/strategy/update/<int:pk>/', views.StrategyUpdateView.as_view(), name='trades_strategy_update'),
)

urlpatterns += (
    # urls for AccountType
    path('trades/accounttype/', views.AccountTypeListView.as_view(), name='trades_accounttype_list'),
    path('trades/accounttype/create/', views.AccountTypeCreateView.as_view(), name='trades_accounttype_create'),
    path('trades/accounttype/detail/<int:pk>/', views.AccountTypeDetailView.as_view(), name='trades_accounttype_detail'),
    path('trades/accounttype/update/<int:pk>/', views.AccountTypeUpdateView.as_view(), name='trades_accounttype_update'),
)

urlpatterns += (
    # urls for Account
    path('trades/account/', views.AccountListView.as_view(), name='trades_account_list'),
    path('trades/account/create/', views.AccountCreateView.as_view(), name='trades_account_create'),
    path('trades/account/detail/<int:pk>/', views.AccountDetailView.as_view(), name='trades_account_detail'),
    path('trades/account/update/<int:pk>/', views.AccountUpdateView.as_view(), name='trades_account_update'),
)

urlpatterns += (
    # urls for Follower
    path('trades/follower/', views.FollowerListView.as_view(), name='trades_follower_list'),
    path('trades/follower/create/', views.FollowerCreateView.as_view(), name='trades_follower_create'),
    path('trades/follower/detail/<int:pk>/', views.FollowerDetailView.as_view(), name='trades_follower_detail'),
    path('trades/follower/update/<int:pk>/', views.FollowerUpdateView.as_view(), name='trades_follower_update'),
)
