import urllib.request
import re

try:
    html = urllib.request.urlopen('https://www.kianagreen.com/').read().decode('utf-8')
    css_files = re.findall(r'href=["\']([^"\']+\.css)["\']', html)
    print("CSS files:", css_files)
    
    all_images = set()
    for css in css_files:
        css_url = 'https://www.kianagreen.com/' + css
        req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/5.0'})
        css_content = urllib.request.urlopen(req).read().decode('utf-8')
        assets = re.findall(r'url\([\'"]?([^"\'\)]+)[\'"]?\)', css_content)
        all_images.update(assets)
        
    print("Images in CSS:")
    for img in sorted(list(all_images)):
        print(img)
except Exception as e:
    print(e)
