"""download the full-size Super Mario Bros maps from nesmaps.com into nesmaps/ (or $NESMAPS)"""
import os, time, urllib.request, http.cookiejar
from paths import NES

SITE = 'https://nesmaps.com/maps/SuperMarioBrothers/'
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36')]
os.makedirs(NES, exist_ok=True)
opener.open(SITE + 'SuperMarioBrosWorld1-1Map.html').read()  # the images need the site's cookie
for w in range(1, 9):
    for n in range(1, 5):
        path = os.path.join(NES, f'{w}-{n}.png')
        if os.path.exists(path):
            continue
        data = opener.open(f'{SITE}SuperMarioBrosMap{w}-{n}.png').read()
        if not data.startswith(b'\x89PNG'):
            raise SystemExit(f'{w}-{n}: nesmaps did not send a PNG, try again later')
        open(path, 'wb').write(data)
        print(path)
        time.sleep(1)
