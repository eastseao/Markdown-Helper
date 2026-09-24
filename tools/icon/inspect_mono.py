from PIL import Image
import numpy as np

m = Image.open("stage/preview/mono.png").convert("RGBA")
a = np.array(m)
alpha = a[..., 3]
print("mono size", m.size, "alpha min/max", alpha.min(), alpha.max(),
      "opaque px", int((alpha > 128).sum()))

# 1) white shape on dark bg
dark = Image.new("RGBA", m.size, (32, 33, 36, 255))
dark.alpha_composite(m)

# 2) tint with a themed colour (Android uses a single tint) - simulate #A8C7FA
tint = Image.new("RGBA", m.size, (255, 255, 255, 0))
ta = np.array(tint)
rgb = np.array(m)
ta[..., 0], ta[..., 1], ta[..., 2] = 0xA8, 0xC7, 0xFA
ta[..., 3] = alpha
tinted = Image.fromarray(ta, "RGBA")
dark2 = Image.new("RGBA", m.size, (32, 33, 36, 255))
dark2.alpha_composite(tinted)

# 3) shrink to 24dp-equivalent (108dp canvas -> 24px) to check legibility
small_white = dark.resize((24, 24), Image.LANCZOS).resize((192, 192), Image.NEAREST)
small_tint = dark2.resize((24, 24), Image.LANCZOS).resize((192, 192), Image.NEAREST)

W = m.size[0]
sheet = Image.new("RGBA", (W * 2 + 60, W + 40), (20, 20, 20, 255))
sheet.paste(dark, (0, 20))
sheet.paste(dark2, (W + 20, 20))
sheet.save("stage/preview/mono_check.png")

sheet2 = Image.new("RGBA", (192 * 2 + 60, 192 + 40), (20, 20, 20, 255))
sheet2.paste(small_white, (0, 20))
sheet2.paste(small_tint, (192 + 20, 20))
sheet2.save("stage/preview/mono_24dp.png")
print("wrote mono_check.png / mono_24dp.png")
