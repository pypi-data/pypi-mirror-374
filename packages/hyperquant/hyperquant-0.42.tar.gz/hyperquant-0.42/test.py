from hyperquant.core import Exchange


e = Exchange([], fee=0)

e.Buy('btc', 100, 1, ts=1234)

print(e['btc'])