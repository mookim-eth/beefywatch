import requests, js2py
from filecache import filecache
sess = requests.session()

@filecache(86400)
def cached_get(url):
    x = sess.get(url)
    assert x.status_code == 200, x
    return x

POOLS = {}
for file in sess.get("https://api.github.com/repos/beefyfinance/beefy-app/contents/src/features/configure/vault").json():
    chain = file['name'].replace("_pools.js", "")
    content = cached_get(file['download_url']).text
    jsondata = "["+content.split("[", 1)[1].rsplit(";",1)[0]
    print("jsondata:", len(jsondata))
    data = js2py.eval_js(jsondata)
    print(len(data))
    POOLS[chain] = data