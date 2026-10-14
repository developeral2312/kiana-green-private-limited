from PIL import Image
import os

screenshot_path = r'C:\Users\dell\.gemini\antigravity-ide\brain\5be169cb-06ff-4582-821a-9390e0cb43c5\.user_uploaded\media_1791463109058.png'
static_dir = r'C:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images'

try:
    img = Image.open(screenshot_path)
    width, height = img.size

    # The products screenshot is very tall.
    # Product 1 (Solar Modules): located around 10-25% of height
    prod1 = img.crop((int(width * 0.05), int(height * 0.11), int(width * 0.95), int(height * 0.22)))
    prod1.save(os.path.join(static_dir, 'product-modules.png'))

    # Product 2 (Inverters): located around 30-45% of height
    prod2 = img.crop((int(width * 0.05), int(height * 0.28), int(width * 0.95), int(height * 0.39)))
    prod2.save(os.path.join(static_dir, 'product-inverters.png'))

    # Product 3 (BESS): located around 50-65% of height
    prod3 = img.crop((int(width * 0.05), int(height * 0.45), int(width * 0.95), int(height * 0.56)))
    prod3.save(os.path.join(static_dir, 'product-bess.png'))

    print("Product images cropped and saved!")
except Exception as e:
    print(f"Error: {e}")
