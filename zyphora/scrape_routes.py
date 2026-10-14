import urllib.request
import re

for route in ['/about', '/products']:
    try:
        url = 'https://www.kianagreen.com' + route
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Look for image URLs in the HTML
        imgs = re.findall(r'(https://images\.unsplash\.com/[^\'"\s]+)', html)
        imgs += re.findall(r'(assets/[^\'"\s]+\.(?:png|jpg|jpeg|webp))', html)
        
        print(f"Images in {route}:")
        for img in set(imgs):
            print(img)
    except Exception as e:
        print(f"Error on {route}: {e}")
