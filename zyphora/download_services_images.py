import urllib.request
import os

images = {
    'services-hero.jpg': 'https://images.unsplash.com/photo-1613665813446-82a78c468a1d?auto=format&fit=crop&w=1920&q=80',
    'services-sourcing.jpg': 'https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?auto=format&fit=crop&w=800&q=80',
    'services-design.jpg': 'https://images.unsplash.com/photo-1521618755572-156ae0cdd74d?auto=format&fit=crop&w=800&q=80',
    'services-install.jpg': 'https://images.unsplash.com/photo-1559302504-64aae6ca6b6f?auto=format&fit=crop&w=800&q=80',
    'services-upgrade.jpg': 'https://images.unsplash.com/photo-1588508493134-8c8502f4f208?auto=format&fit=crop&w=800&q=80',
    'services-maintenance.jpg': 'https://images.unsplash.com/photo-1664273874742-880dbbe90299?auto=format&fit=crop&w=800&q=80',
    'services-inspection.jpg': 'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=800&q=80',
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
