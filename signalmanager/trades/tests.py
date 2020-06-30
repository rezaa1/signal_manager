from django.test import TestCase

# Create your tests here.
# _ auto build
import unittest
from django.urls import reverse
from django.test import Client
from .models import Trade, Broker, Strategy, AccountType, Account, Follower, Symbol, Model71
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {}
    defaults["name"] = "group"
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_trade(**kwargs):
    defaults = {}
    defaults["orderid"] = "orderid"
    defaults["symbol"] = "symbol"
    defaults["type"] = "type"
    defaults["stoploss"] = "stoploss"
    defaults["price"] = "price"
    defaults["units"] = "units"
    defaults["takeprofit"] = "takeprofit"
    defaults["status"] = "status"
    defaults["open_price"] = "open_price"
    defaults["open_time"] = "open_time"
    defaults["error_code"] = "error_code"
    defaults["error_reason"] = "error_reason"
    defaults["close_price"] = "close_price"
    defaults["close_reason"] = "close_reason"
    defaults["close_time"] = "close_time"
    defaults["realizedPL"] = "realizedPL"
    defaults["order_comment"] = "order_comment"
    defaults.update(**kwargs)
    if "account" not in defaults:
        defaults["account"] = create_'account'()
    if "signal" not in defaults:
        defaults["signal"] = create_'signals_signal'()
    if "owner" not in defaults:
        defaults["owner"] = create_'auth_user'()
    return Trade.objects.create(**defaults)


def create_broker(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["description"] = "description"
    defaults.update(**kwargs)
    return Broker.objects.create(**defaults)


def create_strategy(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["description"] = "description"
    defaults["stoploss"] = "stoploss"
    defaults["manage_trade"] = "manage_trade"
    defaults["pending_order"] = "pending_order"
    defaults["break_even"] = "break_even"
    defaults["close_half"] = "close_half"
    defaults["filter_direction"] = "filter_direction"
    defaults["filter_ea_number"] = "filter_ea_number"
    defaults.update(**kwargs)
    return Strategy.objects.create(**defaults)


def create_accounttype(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["environment"] = "environment"
    defaults["description"] = "description"
    defaults.update(**kwargs)
    if "broker" not in defaults:
        defaults["broker"] = create_'broker'()
    return AccountType.objects.create(**defaults)


def create_account(**kwargs):
    defaults = {}
    defaults["account_no"] = "account_no"
    defaults["description"] = "description"
    defaults.update(**kwargs)
    if "type" not in defaults:
        defaults["type"] = create_'accounttype'()
    if "broker" not in defaults:
        defaults["broker"] = create_'broker'()
    if "owner" not in defaults:
        defaults["owner"] = create_'auth_user'()
    return Account.objects.create(**defaults)


def create_follower(**kwargs):
    defaults = {}
    defaults["risk"] = "risk"
    defaults.update(**kwargs)
    if "account" not in defaults:
        defaults["account"] = create_'account'()
    if "channel" not in defaults:
        defaults["channel"] = create_'signals_channel'()
    if "strategy" not in defaults:
        defaults["strategy"] = create_'strategy'()
    if "owner" not in defaults:
        defaults["owner"] = create_'auth_user'()
    return Follower.objects.create(**defaults)


def create_symbol(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Symbol.objects.create(**defaults)


def create_model71(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults.update(**kwargs)
    return Model71.objects.create(**defaults)


class TradeViewTest(unittest.TestCase):
    '''
    Tests for Trade
    '''
    def setUp(self):
        self.client = Client()

    def test_list_trade(self):
        url = reverse('trades_trade_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_trade(self):
        url = reverse('trades_trade_create')
        data = {
            "orderid": "orderid",
            "symbol": "symbol",
            "type": "type",
            "stoploss": "stoploss",
            "price": "price",
            "units": "units",
            "takeprofit": "takeprofit",
            "status": "status",
            "open_price": "open_price",
            "open_time": "open_time",
            "error_code": "error_code",
            "error_reason": "error_reason",
            "close_price": "close_price",
            "close_reason": "close_reason",
            "close_time": "close_time",
            "realizedPL": "realizedPL",
            "order_comment": "order_comment",
            "account": create_'account'().pk,
            "signal": create_'signals_signal'().pk,
            "owner": create_'auth_user'().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_trade(self):
        trade = create_trade()
        url = reverse('trades_trade_detail', args=[trade.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_trade(self):
        trade = create_trade()
        data = {
            "orderid": "orderid",
            "symbol": "symbol",
            "type": "type",
            "stoploss": "stoploss",
            "price": "price",
            "units": "units",
            "takeprofit": "takeprofit",
            "status": "status",
            "open_price": "open_price",
            "open_time": "open_time",
            "error_code": "error_code",
            "error_reason": "error_reason",
            "close_price": "close_price",
            "close_reason": "close_reason",
            "close_time": "close_time",
            "realizedPL": "realizedPL",
            "order_comment": "order_comment",
            "account": create_'account'().pk,
            "signal": create_'signals_signal'().pk,
            "owner": create_'auth_user'().pk,
        }
        url = reverse('trades_trade_update', args=[trade.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class BrokerViewTest(unittest.TestCase):
    '''
    Tests for Broker
    '''
    def setUp(self):
        self.client = Client()

    def test_list_broker(self):
        url = reverse('trades_broker_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_broker(self):
        url = reverse('trades_broker_create')
        data = {
            "name": "name",
            "description": "description",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_broker(self):
        broker = create_broker()
        url = reverse('trades_broker_detail', args=[broker.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_broker(self):
        broker = create_broker()
        data = {
            "name": "name",
            "description": "description",
        }
        url = reverse('trades_broker_update', args=[broker.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class StrategyViewTest(unittest.TestCase):
    '''
    Tests for Strategy
    '''
    def setUp(self):
        self.client = Client()

    def test_list_strategy(self):
        url = reverse('trades_strategy_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_strategy(self):
        url = reverse('trades_strategy_create')
        data = {
            "name": "name",
            "description": "description",
            "stoploss": "stoploss",
            "manage_trade": "manage_trade",
            "pending_order": "pending_order",
            "break_even": "break_even",
            "close_half": "close_half",
            "filter_direction": "filter_direction",
            "filter_ea_number": "filter_ea_number",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_strategy(self):
        strategy = create_strategy()
        url = reverse('trades_strategy_detail', args=[strategy.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_strategy(self):
        strategy = create_strategy()
        data = {
            "name": "name",
            "description": "description",
            "stoploss": "stoploss",
            "manage_trade": "manage_trade",
            "pending_order": "pending_order",
            "break_even": "break_even",
            "close_half": "close_half",
            "filter_direction": "filter_direction",
            "filter_ea_number": "filter_ea_number",
        }
        url = reverse('trades_strategy_update', args=[strategy.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class AccountTypeViewTest(unittest.TestCase):
    '''
    Tests for AccountType
    '''
    def setUp(self):
        self.client = Client()

    def test_list_accounttype(self):
        url = reverse('trades_accounttype_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_accounttype(self):
        url = reverse('trades_accounttype_create')
        data = {
            "name": "name",
            "environment": "environment",
            "description": "description",
            "broker": create_'broker'().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_accounttype(self):
        accounttype = create_accounttype()
        url = reverse('trades_accounttype_detail', args=[accounttype.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_accounttype(self):
        accounttype = create_accounttype()
        data = {
            "name": "name",
            "environment": "environment",
            "description": "description",
            "broker": create_'broker'().pk,
        }
        url = reverse('trades_accounttype_update', args=[accounttype.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class AccountViewTest(unittest.TestCase):
    '''
    Tests for Account
    '''
    def setUp(self):
        self.client = Client()

    def test_list_account(self):
        url = reverse('trades_account_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_account(self):
        url = reverse('trades_account_create')
        data = {
            "account_no": "account_no",
            "description": "description",
            "type": create_'accounttype'().pk,
            "broker": create_'broker'().pk,
            "owner": create_'auth_user'().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_account(self):
        account = create_account()
        url = reverse('trades_account_detail', args=[account.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_account(self):
        account = create_account()
        data = {
            "account_no": "account_no",
            "description": "description",
            "type": create_'accounttype'().pk,
            "broker": create_'broker'().pk,
            "owner": create_'auth_user'().pk,
        }
        url = reverse('trades_account_update', args=[account.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class FollowerViewTest(unittest.TestCase):
    '''
    Tests for Follower
    '''
    def setUp(self):
        self.client = Client()

    def test_list_follower(self):
        url = reverse('trades_follower_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_follower(self):
        url = reverse('trades_follower_create')
        data = {
            "risk": "risk",
            "account": create_'account'().pk,
            "channel": create_'signals_channel'().pk,
            "strategy": create_'strategy'().pk,
            "owner": create_'auth_user'().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_follower(self):
        follower = create_follower()
        url = reverse('trades_follower_detail', args=[follower.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_follower(self):
        follower = create_follower()
        data = {
            "risk": "risk",
            "account": create_'account'().pk,
            "channel": create_'signals_channel'().pk,
            "strategy": create_'strategy'().pk,
            "owner": create_'auth_user'().pk,
        }
        url = reverse('trades_follower_update', args=[follower.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SymbolViewTest(unittest.TestCase):
    '''
    Tests for Symbol
    '''
    def setUp(self):
        self.client = Client()

    def test_list_symbol(self):
        url = reverse('trades_symbol_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_symbol(self):
        url = reverse('trades_symbol_create')
        data = {
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_symbol(self):
        symbol = create_symbol()
        url = reverse('trades_symbol_detail', args=[symbol.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_symbol(self):
        symbol = create_symbol()
        data = {
        }
        url = reverse('trades_symbol_update', args=[symbol.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class Model71ViewTest(unittest.TestCase):
    '''
    Tests for Model71
    '''
    def setUp(self):
        self.client = Client()

    def test_list_model71(self):
        url = reverse('trades_model71_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_model71(self):
        url = reverse('trades_model71_create')
        data = {
            "name": "name",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_model71(self):
        model71 = create_model71()
        url = reverse('trades_model71_detail', args=[model71.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_model71(self):
        model71 = create_model71()
        data = {
            "name": "name",
        }
        url = reverse('trades_model71_update', args=[model71.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


