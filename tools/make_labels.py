"""
Generates the three printable product labels used as MindAR image targets.

Run from the project folder:   python tools/make_labels.py
Output:                        labels/label-0-*.png, label-1-*.png, label-2-*.png

Image tracking finds a label by its "feature points": sharp, high-contrast,
non-repeating detail. So besides the text, every label gets its own pictogram,
a random dot grid and a barcode-style block, all different per label.

The order of LABELS must match products.json (targetIndex 0, 1, 2) and the
order the images are added to the MindAR compiler.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900  # 4 x 3 inches at 300 dpi
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
OUT_DIR = Path(__file__).resolve().parent.parent / "labels"

LABELS = [
    dict(slug="ascorbic-acid", name="ASCORBIC ACID", grade="USP  |  Vitamin C  |  Fine Powder",
         item="RM-10421", lot="ASC-24117", net="25 kg", accent=(30, 90, 168), icon="sun"),
    dict(slug="microcrystalline-cellulose", name="MICROCRYSTALLINE CELLULOSE", grade="NF  |  PH-102  |  Excipient",
         item="RM-20388", lot="MCC-24302", net="20 kg", accent=(107, 63, 160), icon="hex"),
    dict(slug="citric-acid", name="CITRIC ACID", grade="Anhydrous  |  Food Grade  |  Granular",
         item="RM-30156", lot="CIT-23088", net="25 kg", accent=(60, 60, 60), icon="crystal"),
]


def font(size, bold=False):
    path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size)  # non-Windows fallback


def fit_font(draw, text, max_width, size, bold=True):
    """Largest font (starting at `size`) that fits `text` in `max_width` pixels."""
    while size > 20 and draw.textlength(text, font=font(size, bold)) > max_width:
        size -= 2
    return font(size, bold)


def draw_header(d, label, index):
    """Coloured band across the top. Each label has a different right-hand pattern."""
    x0, y0, x1, y1 = 20, 20, W - 20, 150
    d.rectangle([x0, y0, x1, y1], fill=label["accent"])
    d.text((50, 50), "RAW MATERIAL", font=font(56, True), fill=WHITE)
    if index == 1:    # diagonal stripes
        for x in range(760, x1 + 130, 44):
            d.polygon([(x, y0), (x + 22, y0), (x - 108, y1), (x - 130, y1)], fill=WHITE)
        d.rectangle([x1, y0, W, y1], fill=WHITE)
    elif index == 2:  # row of circles
        for i, x in enumerate(range(780, x1 - 40, 70)):
            r = 26 if i % 2 == 0 else 16
            d.ellipse([x - r, 85 - r, x + r, 85 + r], fill=WHITE)
    else:             # stepped blocks
        for i, x in enumerate(range(780, x1 - 30, 64)):
            h = 30 + (i * 23) % 80
            d.rectangle([x, y1 - h - 10, x + 40, y1 - 10], fill=WHITE)


def draw_icon(d, kind, cx, cy, accent):
    """Big pictogram on the left side of the label."""
    if kind == "sun":      # citrus slice / sun: ring of triangular rays
        for i in range(12):
            a = i * math.pi / 6
            tip = (cx + 170 * math.cos(a), cy + 170 * math.sin(a))
            l = (cx + 105 * math.cos(a - 0.22), cy + 105 * math.sin(a - 0.22))
            r = (cx + 105 * math.cos(a + 0.22), cy + 105 * math.sin(a + 0.22))
            d.polygon([tip, l, r], fill=BLACK)
        d.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], fill=accent)
        d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=WHITE)
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=BLACK)
    elif kind == "hex":    # honeycomb, like a cellulose ring structure
        r = 52
        centres = [(0, 0), (1, 0), (-1, 0), (0.5, 1), (-0.5, 1), (0.5, -1), (-0.5, -1)]
        for i, (gx, gy) in enumerate(centres):
            hx, hy = cx + gx * r * 1.8, cy + gy * r * 1.56
            pts = [(hx + r * math.cos(math.pi / 6 + k * math.pi / 3),
                    hy + r * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
            d.polygon(pts, fill=accent if i % 3 == 0 else WHITE, outline=BLACK, width=8)
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=BLACK)
    else:                  # crystal: stacked diamonds and triangles
        d.polygon([(cx, cy - 170), (cx + 120, cy), (cx, cy + 170), (cx - 120, cy)], fill=BLACK)
        d.polygon([(cx, cy - 110), (cx + 75, cy), (cx, cy + 110), (cx - 75, cy)], fill=WHITE)
        d.polygon([(cx, cy - 60), (cx + 40, cy), (cx, cy + 60), (cx - 40, cy)], fill=accent)
        d.polygon([(cx - 165, cy + 170), (cx - 120, cy + 80), (cx - 75, cy + 170)], fill=BLACK)
        d.polygon([(cx + 75, cy - 170), (cx + 120, cy - 80), (cx + 165, cy - 170)], fill=BLACK)


def draw_barcode(d, rng, x0, y0, x1, y1):
    """Barcode-STYLE block (random bars, not a scannable symbology)."""
    x = x0
    while x < x1:
        w = rng.choice([4, 4, 6, 8, 12])
        if x + w > x1:
            break
        d.rectangle([x, y0, x + w - 1, y1], fill=BLACK)
        x += w + rng.choice([4, 6, 8, 10])


def draw_dot_grid(d, rng, x0, y0, cell, n):
    """Random square grid with three solid corner markers (QR-like, not a real QR)."""
    for gy in range(n):
        for gx in range(n):
            if rng.random() < 0.5:
                d.rectangle([x0 + gx * cell, y0 + gy * cell, x0 + (gx + 1) * cell - 1, y0 + (gy + 1) * cell - 1], fill=BLACK)
    for mx, my in [(0, 0), (n - 3, 0), (0, n - 3)]:
        px, py = x0 + mx * cell, y0 + my * cell
        d.rectangle([px, py, px + 3 * cell - 1, py + 3 * cell - 1], fill=BLACK)
        d.rectangle([px + cell // 2, py + cell // 2, px + 3 * cell - cell // 2 - 1, py + 3 * cell - cell // 2 - 1], fill=WHITE)
        d.rectangle([px + cell, py + cell, px + 2 * cell - 1, py + 2 * cell - 1], fill=BLACK)


def make_label(index, label):
    rng = random.Random(label["lot"])  # seeded, so re-running gives identical labels
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    draw_header(d, label, index)
    draw_icon(d, label["icon"], 215, 370, label["accent"])

    # Text column on the right
    tx, tw = 420, W - 60 - 420
    words = label["name"].split()
    lines = [label["name"]] if len(words) == 1 or d.textlength(label["name"], font=font(76, True)) <= tw \
        else [words[0], " ".join(words[1:])]
    y = 180
    for line in lines:
        f = fit_font(d, line, tw, 76)
        d.text((tx, y), line, font=f, fill=BLACK)
        y += f.size + 8
    d.text((tx, y + 4), label["grade"], font=fit_font(d, label["grade"], tw, 38, bold=False), fill=BLACK)
    d.text((tx, y + 62), f"Item {label['item']}     Net {label['net']}", font=font(36), fill=BLACK)

    # Lot number in a bold box (the human-readable key a worker would check)
    d.rectangle([tx, 470, W - 60, 570], outline=BLACK, width=6)
    d.text((tx + 24, 487), "LOT", font=font(64, True), fill=label["accent"])
    d.text((tx + 180, 487), label["lot"], font=font(64, True), fill=BLACK)

    # Bottom row: barcode-style block + random dot grid
    draw_barcode(d, rng, 50, 610, 820, 780)
    lot_text = "*" + label["lot"].replace("-", "") + "*"
    d.text((50, 790), lot_text, font=font(36, True), fill=BLACK)
    draw_dot_grid(d, rng, 880, 600, 26, 10)

    d.text((50, 845), "SAMPLE LABEL  |  CSC 633 AR DEMO  |  FICTIONAL DATA", font=font(26), fill=BLACK)

    # Thick outer border, drawn last so nothing paints over it
    d.rectangle([8, 8, W - 9, H - 9], outline=BLACK, width=12)

    out = OUT_DIR / f"label-{index}-{label['slug']}.png"
    img.save(out, dpi=(300, 300))
    print("wrote", out)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    for i, lab in enumerate(LABELS):
        make_label(i, lab)
