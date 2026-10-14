import urllib.request
import re

try:
    html = urllib.request.urlopen('https://www.kianagreen.com/').read().decode('utf-8')
    js_files = re.findall(r'src=["\']([^"\']+\.js)["\']', html)
    print("JS files:", js_files)
    
    all_images = set()
    for js in js_files:
        js_url = 'https://www.kianagreen.com/' + js
        req = urllib.request.Request(js_url, headers={'User-Agent': 'Mozilla/5.0'})
        js_content = urllib.request.urlopen(req).read().decode('utf-8')
        assets = re.findall(r'(assets/[^"\'\s]+\.(?:png|jpg|jpeg|svg|webp))', js_content)
        all_images.update(assets)
        
    print("All images found:")
    for img in sorted(list(all_images)):
        print("https://www.kianagreen.com/" + img)
except Exception as e:
    print(e)
