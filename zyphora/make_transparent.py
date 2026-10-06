from PIL import Image
import os

img_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images\logo1.png"
out_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images\logo_transparent.png"

try:
    img = Image.open(img_path)
    img = img.convert("RGBA")
    
    datas = img.getdata()
    new_data = []
    
    # We will make white (and near white) transparent
    for item in datas:
        # If it's very bright (near white background), make it transparent
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(out_path, "PNG")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
