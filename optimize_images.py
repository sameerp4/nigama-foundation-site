#!/usr/bin/env python3
"""One-shot image optimizer for the Nigama Foundation static site.
Recompresses raster images in place, preserving filename & format so no HTML/CSS
references need to change. Caps max dimension at 2000px, JPEG q82 progressive,
PNG optimized (palette-quantized when it has no meaningful alpha)."""
import os
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
MAX_DIM = 2000
JPEG_Q = 82

def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

def has_alpha(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        a = im.convert("RGBA").getchannel("A")
        return a.getextrema()[0] < 255
    return False

paths = []
for root, _dirs, files in os.walk(IMG_DIR):
    for fn in files:
        if os.path.splitext(fn)[1].lower() in (".jpg", ".jpeg", ".png"):
            paths.append(os.path.join(root, fn))

rows = []
before_total = after_total = 0
for path in sorted(paths):
    name = os.path.relpath(path, IMG_DIR)
    ext = os.path.splitext(path)[1].lower()
    before = os.path.getsize(path)
    before_total += before
    try:
        im = Image.open(path)
        im.load()
    except Exception as e:
        print(f"SKIP {name}: {e}")
        after_total += before
        continue

    # Skip files already within cap and already small (avoids generational recompression)
    if before <= 250 * 1024 and max(im.size) <= MAX_DIM:
        after_total += before
        continue

    # Fix orientation from EXIF, then downscale
    from PIL import ImageOps
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

    if ext in (".jpg", ".jpeg"):
        im = im.convert("RGB")
        im.save(path, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    else:  # PNG
        if has_alpha(im):
            im = im.convert("RGBA")
            im.save(path, "PNG", optimize=True)
        else:
            # No transparency: quantize to palette for big savings, stays .png
            im = im.convert("RGB").quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
            im.save(path, "PNG", optimize=True)

    after = os.path.getsize(path)
    after_total += after
    if before - after > 20 * 1024:
        rows.append((name, before, after))

rows.sort(key=lambda r: r[1] - r[2], reverse=True)
print(f"{'image':<42}{'before':>10}{'after':>10}{'saved':>10}")
for name, b, a in rows:
    print(f"{name:<42}{human(b):>10}{human(a):>10}{human(b-a):>10}")
print("-" * 72)
print(f"{'TOTAL':<42}{human(before_total):>10}{human(after_total):>10}{human(before_total-after_total):>10}")
