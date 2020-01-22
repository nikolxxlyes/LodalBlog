def get_currency_pair():
    import requests
    url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
    r = requests.get(url)
    # print(r.status_code)

    if r.status_code == 200:
        exchange = r.json()
    else:
        return None

    current_pairs = [{'currency_pair':money['ccy']+'/'+money['base_ccy'],
                      'buy':round(float(money['buy']),2),
                    'sale':round(float(money['sale']),2)} for money in exchange]

    return current_pairs

def set_currency_pair(db,ExchangeRate):
    import warnings
    current_pairs = get_currency_pair()
    if current_pairs is None:
        warnings.warn("Exchange pairs wasn's loaded. Perhaps, BAD CONNECTION!!!")
        return
    old_pairs = ExchangeRate.query.all()
    if old_pairs:
        for old_pair in old_pairs:
            db.session.delete(old_pair)
        db.session.commit()
    pairs = [ExchangeRate(currency_pair=pair['currency_pair'],buy=pair['buy'],sale=pair['sale']) for pair in current_pairs]
    db.session.add_all(pairs)
    db.session.commit()
