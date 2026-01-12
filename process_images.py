import os
from PIL import Image

def remove_background(image_path):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # Use a threshold to catch near-white pixels if necessary
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(image_path, "PNG")

directory = r"C:\Users\lulef\.gemini\antigravity\brain\4fd1bd83-a2c0-4dbe-93e9-99432fb42ede"
for filename in os.listdir(directory):
    if filename.startswith("rabbit") and filename.endswith(".png"):
        print(f"Processing {filename}...")
        remove_background(os.path.join(directory, filename))
