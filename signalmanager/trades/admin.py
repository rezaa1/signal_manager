from django.contrib import admin

# Register your models here.
#_ auto build


from django.contrib import admin
from django import forms
from .models import Trade, Broker, Strategy, AccountType, Account, Follower
class TradeAdminForm(forms.ModelForm):

    class Meta:
        model = Trade
        fields = '__all__'


class TradeAdmin(admin.ModelAdmin):
    form = TradeAdminForm
    list_display = ['created', 'orderid', 'symbol', 'type', 'stoploss', 'price', 'units', 'takeprofit', 'status', 'open_price', 'open_time', 'error_code', 'error_reason', 'close_price', 'close_reason', 'close_time', 'realizedPL', 'order_comment']
    readonly_fields = ['created', 'orderid', 'symbol', 'type', 'stoploss', 'price', 'units', 'takeprofit', 'status', 'open_price', 'open_time', 'error_code', 'error_reason', 'close_price', 'close_reason', 'close_time', 'realizedPL', 'order_comment']

admin.site.register(Trade, TradeAdmin)


class BrokerAdminForm(forms.ModelForm):

    class Meta:
        model = Broker
        fields = '__all__'


class BrokerAdmin(admin.ModelAdmin):
    form = BrokerAdminForm
    list_display = ['name', 'description']
    readonly_fields = ['name', 'description']

admin.site.register(Broker, BrokerAdmin)


class StrategyAdminForm(forms.ModelForm):

    class Meta:
        model = Strategy
        fields = '__all__'


class StrategyAdmin(admin.ModelAdmin):
    form = StrategyAdminForm
    list_display = ['name', 'description', 'stoploss', 'manage_trade', 'pending_order', 'break_even', 'close_half', 'filter_direction', 'filter_ea_number']
    readonly_fields = ['name', 'description', 'stoploss', 'manage_trade', 'pending_order', 'break_even', 'close_half', 'filter_direction', 'filter_ea_number']

admin.site.register(Strategy, StrategyAdmin)


class AccountTypeAdminForm(forms.ModelForm):

    class Meta:
        model = AccountType
        fields = '__all__'


class AccountTypeAdmin(admin.ModelAdmin):
    form = AccountTypeAdminForm
    list_display = ['name', 'environment', 'description']
    readonly_fields = ['name', 'environment', 'description']

admin.site.register(AccountType, AccountTypeAdmin)


class AccountAdminForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = '__all__'


class AccountAdmin(admin.ModelAdmin):
    form = AccountAdminForm
    list_display = ['created', 'account_no', 'description']
    readonly_fields = ['created', 'account_no', 'description']

admin.site.register(Account, AccountAdmin)


class FollowerAdminForm(forms.ModelForm):

    class Meta:
        model = Follower
        fields = '__all__'


class FollowerAdmin(admin.ModelAdmin):
    form = FollowerAdminForm
    list_display = ['created', 'risk']
    readonly_fields = ['created', 'risk']

admin.site.register(Follower, FollowerAdmin)


