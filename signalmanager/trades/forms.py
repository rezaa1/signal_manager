
from django.forms import ModelForm,ModelChoiceField
from django.forms import modelformset_factory,inlineformset_factory
from django.shortcuts import render

from .models import *
from signals.models import Channel

# Create the form class.


class AccountModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "My Object #%i" % obj.name

class FollowerForm(ModelForm):
     class Meta:
         model = Follower
         # account = AccountModelChoiceField(queryset=Account.objects.filter(pk=3).order_by('name'))
         fields = '__all__'
         #exclude = ('owner',)

     def __init__(self , *args, **kwargs):
        super(FollowerForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.values("account_no","description")
        self.fields['strategy'].queryset = Strategy.objects.all().values("name")
        self.fields['channel'].queryset = Channel.objects.values("title")



class AccountForm(ModelForm):
     class Meta:
         model = Account
         # account = AccountModelChoiceField(queryset=Account.objects.filter(pk=3).order_by('name'))
         fields = '__all__'
         #exclude = ('owner',)

     # def __init__(self , *args, **kwargs):
     #    super(AccountForm, self).__init__(*args, **kwargs)
     #    self.fields['type'].queryset = AccountType.objects.values("name")
     #    self.fields['broker'].queryset = Broker.objects.values("name")


# Creating a form to add an article.

# Creating a form to change an existing article.
# def 
# article = Follower.objects.get(pk=1)
# form =FollowerForm(instance=article)


def manage_follower(request):
    #FollowerFormSet = modelformset_factory(Follower,fields=("__all__"))
    if request.method == 'POST':
        formset = FollowerForm(request.POST)
        
        if formset.is_valid():

            post = formset.save(commit=False)
            print(dir(post))
            post.save()
            # formset.save()
            # do something.
    else:
        formset = FollowerForm()
    return render(request, 'manage_follower.html', {'formset': formset})



def manage_account(request):
    #FollowerFormSet = modelformset_factory(Follower,fields=("__all__"))
    if request.method == 'POST':
        formset = AccountForm(request.POST)
        
        if formset.is_valid():

            post = formset.save(commit=False)
            print(dir(post))
            post.save()
            # formset.save()
            # do something.
    else:
        formset = AccountForm()
    return render(request, 'manage_follower.html', {'formset': formset})



# class FollowerForm(ModelForm):

#     class Meta:
#         model = CollectionTitle
#         exclude = ()

# FolloweFormSet = inlineformset_factory(
#     Follower, CollectionTitle, form=CollectionTitleForm,
#     fields=['name', 'language'], extra=1, can_delete=True
#     )

###_________________ auto build
from django import forms
from .models import Trade, Broker, Strategy, AccountType, Account, Follower


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['orderid', 'symbol', 'type', 'stoploss', 'price', 'units', 'takeprofit', 'status', 'open_price', 'open_time', 'error_code', 'error_reason', 'close_price', 'close_reason', 'close_time', 'realizedPL', 'order_comment', 'account', 'signal', 'owner']


class BrokerForm(forms.ModelForm):
    class Meta:
        model = Broker
        fields = ['name', 'description']


class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        #fields = ['name', 'description', 'stoploss', 'manage_trade', 'pending_order', 'break_even', 'close_half', 'filter_direction', 'filter_ea_number']
        fields = '__all__'

class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ['name', 'environment', 'description', 'broker']


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_no', 'description', 'type', 'broker', 'token' , 'owner']


class FollowerForm(forms.ModelForm):
    class Meta:
        model = Follower
        fields = ['risk', 'account', 'channel', 'strategy', 'owner','size_multiplier']
