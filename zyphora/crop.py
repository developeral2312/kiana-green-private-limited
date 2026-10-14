from PIL import Image
import os

screenshot_path = r'C:\Users\dell\.gemini\antigravity-ide\brain\5be169cb-06ff-4582-821a-9390e0cb43c5\.user_uploaded\media_1791462942911.png'
static_dir = r'C:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images'

img = Image.open(screenshot_path)
width, height = img.size

# Hero image (top section). Let's approximate the crop box. 
# Usually hero is full width, top 0 to some height.
hero = img.crop((0, 0, width, int(width * 0.35)))
hero.save(os.path.join(static_dir, 'about-hero.png'))

# Middle image 1 (Worker drilling). It's located roughly after the text.
# Let's crop a middle section.
worker = img.crop((int(width * 0.05), int(height * 0.15), int(width * 0.95), int(height * 0.28)))
worker.save(os.path.join(static_dir, 'about-worker.png'))

# Middle image 2 (Rooftop panels).
rooftop = img.crop((int(width * 0.05), int(height * 0.32), int(width * 0.95), int(height * 0.45)))
rooftop.save(os.path.join(static_dir, 'about-rooftop.png'))

print("Images cropped and saved!")
