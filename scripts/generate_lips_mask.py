from PIL import Image, ImageDraw

# Generate a mask 512x256 with transparent background and a black lips silhouette
W, H = 512, 256
img = Image.new('RGBA', (W, H), (0,0,0,0))
d = ImageDraw.Draw(img)

# Draw an approximate lips silhouette using bezier-like polygons and ellipses
# Top lip
d.polygon([
    (64,128), (96,88), (160,64), (256,64), (352,64), (416,88), (448,128),
    (416,160), (352,184), (256,184), (160,184), (96,160)
], fill=(0,0,0,255))

# Cut a subtle inner mouth to make shape more lip-like (erase area)
mask = Image.new('L', (W,H), 0)
md = ImageDraw.Draw(mask)
md.ellipse((150,100,362,156), fill=255)
img.putalpha(ImageChops.subtract(img.split()[-1], mask))

# Save trimmed to content bbox for tighter sampling
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)
    # Optionally add small padding to avoid clipping
    pad = 8
    new = Image.new('RGBA', (img.width+pad*2, img.height+pad*2), (0,0,0,0))
    new.paste(img, (pad,pad))
    img = new

out_path = 'static/assets/masks/lips_gold.png'
img.save(out_path, 'PNG')
print('Wrote', out_path)
