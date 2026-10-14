import urllib.request
import os

images = {
    'about-hero-hd.jpg': 'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=1920&q=80',
    'about-worker-hd.jpg': 'https://images.unsplash.com/photo-1559302504-64aae6ca6b6f?auto=format&fit=crop&w=800&q=80',
    'about-rooftop-hd.jpg': 'https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?auto=format&fit=crop&w=800&q=80',
    'product-hero-hd.jpg': 'https://images.unsplash.com/photo-1521618755572-156ae0cdd74d?auto=format&fit=crop&w=1920&q=80',
    'product-modules-hd.jpg': 'https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?auto=format&fit=crop&w=800&q=80',
    'product-inverters-hd.jpg': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80',
    'product-bess-hd.jpg': 'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=800&q=80',
}

static_dir = r'C:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images'

for name, url in images.items():
    path = os.path.join(static_dir, name)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
