def getPriceDetail(account,token,params):
    r = pricing.PricingInfo(accountID=account, params=params)
    api = oandapyV20.API(access_token=token)
    rv = api.request(r)
    res=rv['prices']
    x=[]
    for rv in res:
#        print(rv)
        bid=rv['bids'][0]['price']
        ask=rv['asks'][0]['price']
        qhcf_n=rv["quoteHomeConversionFactors"]['negativeUnits']
        ins=rv['instrument']
        x.append({"ins":ins,"bid": bid, "ask": ask,"quoteHomeConversionFactor":qhcf_n})
    return(x)


symbol="EUR_USD,NAS100_USD"
token="6207e967d6ee40aad284e1f856139755-1462bb1f9d5c4e516c2a2e07c3e0e1d5" #trmm
account="101-001-8394451-001"
import json
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
api = oandapyV20.API(access_token=token)
#params = {_v3_accounts_accountID_pricing_stream_params}
params = { "instruments" : symbol}

#print(getPriceDetail(account,token,params))

r = pricing.PricingStream(accountID=account, params=params)
rv = api.request(r)
maxrecs = 10000
print(dir(rv))
t=0
for ticks in rv:
  if ticks["type"] == "PRICE":
    data=dict(instrument=ticks["instrument"],time=ticks["time"],bids=[ticks["bids"][0]["price"]], asks=[ticks["asks"][0]["price"]],closeoutBid=ticks["closeoutBid"],closeoutAsk=ticks["closeoutAsk"])
    print(data)
 # print(json.dumps(ticks, indent=4),",")
  if t > maxrecs:
    break



