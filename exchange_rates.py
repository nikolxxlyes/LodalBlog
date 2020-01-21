import requests

url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
r = requests.get(url)
print(r.status_code)

if r.status_code == 200:
    exchange = r.json()

print(exchange)

current_rates = [{'currency_pair':money['ccy']+'/'+money['base_ccy'],
                  'buy':round(float(money['buy']),2),
                  'sale':round(float(money['sale']),2)} for money in exchange]

print(current_rates)
