from notebook_models import ExampleModelToken
ExampleModelToken.objects.using('notebook_app').create(name='Bitcoin',
    symbol='btc', price_usd=100000)
example_model_token_set = ExampleModelToken.objects.using('notebook_app').all()
for example_model_token_obj in example_model_token_set:
    name = example_model_token_obj.name
    symbol = example_model_token_obj.symbol
    price_usd = example_model_token_obj.price_usd
    print(f'Instrument {name} with symbol {symbol} has price {price_usd}')

#END OF QUBE
