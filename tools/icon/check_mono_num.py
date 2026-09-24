from PIL import Image
import numpy as np
m = np.array(Image.open("stage/preview/mono.png").convert("RGBA"))
a = m[..., 3]
tot = a.size
bins = {"0 (transparent)": (a == 0), "1-254 (partial)": (a > 0) & (a < 255), "255 (solid)": (a == 255)}
for k, v in bins.items():
    print(f"  {k:20s} {int(v.sum()):7d}  {v.sum()/tot:6.2%}")
# only the doc's outer edge should be partial; a large partial count means ghost features
edge = int(((a > 0) & (a < 255)).sum())
print(f"  partial pixels {edge} -> {'OK (edge AA only)' if edge < 25000 else 'CHECK: too many'}")
