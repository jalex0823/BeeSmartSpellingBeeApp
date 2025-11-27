from PIL import Image
import numpy as np

# Check the gold mask file
fname = 'static/assets/visualizer/lips_mask_gold.png'
img = Image.open(fname)
arr = np.array(img)

print(f'📊 {fname}:')
print(f'   Shape: {arr.shape}')
print(f'   Data type: {arr.dtype}')

# Analyze pixel values
if len(arr.shape) == 3:
    if arr.shape[2] >= 4:
        r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    else:
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        a = np.ones_like(r) * 255
    
    brightness = (r.astype(float) + g.astype(float) + b.astype(float)) / 3
    
    print(f'   Brightness: min={brightness.min():.0f}, max={brightness.max():.0f}, mean={brightness.mean():.0f}')
    print(f'   Alpha: min={a.min()}, max={a.max()}')
    
    # Count pixels at different thresholds
    for thresh in [10, 30, 50, 60, 100, 150, 200]:
        count = ((brightness > thresh) & (a > 10)).sum()
        print(f'   Pixels > {thresh} brightness (a>10): {count}')
    
    # Check what's at the extreme values
    black_pixels = (brightness < 30).sum()
    gold_pixels = (brightness > 100).sum()
    print(f'\n   Black pixels (brightness<30): {black_pixels}')
    print(f'   Gold pixels (brightness>100): {gold_pixels}')
