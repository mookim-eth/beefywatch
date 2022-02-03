import requests, js2py, json, sys
from filecache import filecache
sess = requests.session()

@filecache(86400)
def cached_get(url):
    x = sess.get(url)
    assert x.status_code == 200, x
    return x

@filecache(600)
def cached_get600(url):
    x = sess.get(url)
    assert x.status_code == 200, x
    return x

POOLS = {}
FULL = {}
for file in cached_get600("https://api.github.com/repos/beefyfinance/beefy-app/contents/src/features/configure/vault").json():
    chain = file['name'].replace("_pools.js", "")
    content = cached_get(file['download_url']).text
    jsondata = "["+content.split("[", 1)[1].rsplit(";",1)[0]
    data = js2py.eval_js(jsondata)
    print(chain, len(data), file=sys.stderr)
    for i in data:
        i['chain'] = chain
        FULL[i['id']] = i
    POOLS[chain] = data

PRICES = cached_get600("https://api.beefy.finance/prices").json()
APY = cached_get600("https://api.beefy.finance/apy/breakdown").json()
FR=json.load(open("fundingrate.cache"))#this part use binance api to fetch u-Contract funding rate, TODO: open-source this code
STABLES = [i.strip() for i in open("stablecoins.txt")]

def getapy(id):
    if id not in APY:
        return 0
    apy = APY[id]['totalApy']
    if 'vaultApr' in APY[id]:
        apy = APY[id]['vaultApr']
    return apy

PURESTABLES = []
HEDGED = []
for chain, data in POOLS.items():
    for i in data:
        id = i["id"]
        if id.endswith("-eol") or id not in APY:
            continue
        assets = i['assets']
        if all(i in STABLES for i in assets):
            PURESTABLES.append([chain, i['platform'], "-".join(assets), getapy(id)])
        else:
            notstables = [i for i in assets if i not in STABLES]
            if len(notstables)==1 and notstables[0].upper() in FR:
                coin = notstables[0].upper()
                HEDGED.append([chain, i['platform'], "-".join(assets), (getapy(id)+FR[coin]/100)])

print("Pure Stables APY Top10:")
for i in sorted(PURESTABLES, key=lambda i:i[-1], reverse=True)[:10]:
    print(*i, sep="\t")

HEDGE_RATIO = 0.5
print(f"Hedged APY Top10: (Hedge Ratio: {HEDGE_RATIO})")
for i in sorted(HEDGED, key=lambda i:i[-1], reverse=True)[:10]:
    i[-1] *= HEDGE_RATIO
    print(*i, sep="\t")