from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W = H = 1200
img = Image.new("RGBA", (W, H), (250, 248, 245, 255))

# ── helpers ──────────────────────────────────────────────
def rgba(r, g, b, a=255):
    return (r, g, b, a)

nude      = rgba(240, 224, 214)
blush     = rgba(232, 196, 184)
champagne = rgba(212, 175, 122)
gold      = rgba(201, 169, 110)
dark      = rgba(58,  50,  40)
medium    = rgba(107, 91,  78)
light     = rgba(156, 136, 128)
white     = rgba(255, 255, 255)

def layer():
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return l, ImageDraw.Draw(l)

def composite(base, over):
    return Image.alpha_composite(base, over)

def pill_shape(d, cx, hw, top, bot, fill):
    """Filled vertical pill/stadium shape."""
    d.ellipse([cx-hw, top,      cx+hw, top+hw*2], fill=fill)
    mid_top = top + hw
    mid_bot = bot  - hw
    if mid_bot > mid_top:
        d.rectangle([cx-hw, mid_top, cx+hw, mid_bot], fill=fill)
    d.ellipse([cx-hw, bot-hw*2, cx+hw, bot],          fill=fill)

def pill_outline(d, cx, hw, top, bot, color, w=1):
    d.arc([cx-hw, top, cx+hw, top+hw*2], 180, 0, fill=color, width=w)
    mid_top = top + hw
    mid_bot = bot  - hw
    if mid_bot > mid_top:
        d.line([(cx-hw, mid_top), (cx-hw, mid_bot)], fill=color, width=w)
        d.line([(cx+hw, mid_top), (cx+hw, mid_bot)], fill=color, width=w)
    d.arc([cx-hw, bot-hw*2, cx+hw, bot], 0, 180, fill=color, width=w)

def draw_sparkle(d, cx, cy, size, color):
    d.line([(cx, cy - size), (cx, cy + size)], fill=color, width=1)
    d.line([(cx - size, cy), (cx + size, cy)], fill=color, width=1)
    s = int(size * 0.65)
    d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=color, width=1)
    d.line([(cx + s, cy - s), (cx - s, cy + s)], fill=color, width=1)

def arc_pts(cx, cy, rx, ry, a0, a1, n=120):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts

def draw_curve(d, pts, color, width=1):
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i+1]], fill=color, width=width)

def centered_x(draw_obj, text, font):
    bb = draw_obj.textbbox((0, 0), text, font=font)
    return (W - (bb[2] - bb[0])) // 2

# ── LAYER 1: background gradient ─────────────────────────
bg, bgd = layer()
for y in range(H):
    t = y / H
    r = int(250 * (1-t) + 237 * t)
    g = int(248 * (1-t) + 221 * t)
    b = int(245 * (1-t) + 213 * t)
    bgd.line([(0, y), (W, y)], fill=(r, g, b, 255))
img = composite(img, bg)

# ── LAYER 2: large soft ambient circles ──────────────────
c1, c1d = layer()
c1d.ellipse([780, -120, 1380, 480], fill=(*blush[:3], 38))
c1d.ellipse([820, -60,  1310, 410], fill=(*nude[:3],  28))
c1d.ellipse([-130, 720, 420, 1270], fill=(*nude[:3],  32))
c1d.ellipse([-70,  775, 370, 1215], fill=(*blush[:3], 22))
img = composite(img, c1)

# ── LAYER 3: thin arc decorations ────────────────────────
arcs, arcsd = layer()
arc_color = (*champagne[:3], 18)
draw_curve(arcsd, arc_pts(600, 300, 720, 420, -175, -5),  arc_color)
draw_curve(arcsd, arc_pts(600, 820, 720, 420,    5, 175), arc_color)
draw_curve(arcsd, arc_pts(600, 300, 560, 320, -175, -5),  (*champagne[:3], 12))
draw_curve(arcsd, arc_pts(600, 820, 560, 320,    5, 175), (*champagne[:3], 12))
img = composite(img, arcs)

# ── LAYER 4: scattered gold dots ─────────────────────────
dots_l, dots_d = layer()
dot_data = [
    (170, 148, 4, 72), (1000, 218, 3,   62),
    (138, 680, 3,  56), (1055, 595, 4,  68),
    (215, 990, 3,  60), (1030, 948, 3,  54),
    (75,  405, 2.5, 46), (1108, 398, 2.5, 46),
    (355, 118, 3,  66), (858, 128,  2.5, 56),
    (95,  1095, 2.5, 50), (1098, 1092, 2.5, 50),
    (430, 68,  2,  50), (775, 62,   2,  50),
]
for (x, y, r, a) in dot_data:
    r = int(r)
    dots_d.ellipse([x-r, y-r, x+r, y+r], fill=(*champagne[:3], a))
img = composite(img, dots_l)

# ── LAYER 5: sparkle accents ─────────────────────────────
sp_l, sp_d = layer()
sp_color = (*gold[:3], 130)
draw_sparkle(sp_d, 458, 168, 14, sp_color)
draw_sparkle(sp_d, 748, 290, 10, sp_color)
draw_sparkle(sp_d, 444, 372, 8,  (*champagne[:3], 110))
draw_sparkle(sp_d, 762, 155, 8,  (*champagne[:3], 100))
# tiny solo dots near illustration
for (x, y, r) in [(506, 255, 3), (694, 192, 3), (720, 375, 3), (488, 408, 3)]:
    sp_d.ellipse([x-r, y-r, x+r, y+r], fill=(*gold[:3], 120))
img = composite(img, sp_l)

# ── LAYER 6: nail polish bottle illustration ──────────────
# All measurements: center x = 600
bx = 600

# --- geometry ---
body_hw   = 58   # half-width of bottle body
body_top  = 192
body_bot  = 430
body_r    = 26   # corner radius approximation

neck_hw   = 22
neck_top  = 142
neck_bot  = 196

cap_hw    = 22
cap_top   = 98
cap_bot   = 155
cap_r     = 9

brush_hw  = 5
brush_top = 50
brush_bot = 104

bottle_l, bd = layer()

# -- bottle body --
pill_shape(bd, bx, body_hw, body_top, body_bot, (*nude[:3], 212))

# -- liquid fill --
liq_top = body_top + 100
pill_shape(bd, bx, body_hw - 12, liq_top, body_bot - 10, (224, 152, 152, 55))

# -- shoulder band --
bd.ellipse([bx-body_hw, neck_bot-10, bx+body_hw, neck_bot+10],
           fill=(*blush[:3], 70))

# -- neck --
bd.rectangle([bx-neck_hw, neck_top, bx+neck_hw, neck_bot],
             fill=(248, 242, 235, 225))

# -- cap --
pill_shape(bd, bx, cap_hw, cap_top, cap_bot, (*champagne[:3], 178))

# -- brush handle --
bd.rectangle([bx-brush_hw, brush_top, bx+brush_hw, brush_bot],
             fill=(*gold[:3], 160))
bd.ellipse([bx-brush_hw-2, brush_top-14, bx+brush_hw+2, brush_top+2],
           fill=(*gold[:3], 145))

# -- highlights --
hl_x1 = bx - body_hw + 7
hl_x2 = bx - body_hw + 13
mid_top = body_top + body_hw + 10
mid_bot = body_bot - body_hw - 15
if mid_bot > mid_top:
    bd.rectangle([hl_x1, mid_top, hl_x2, mid_bot], fill=(255, 255, 255, 55))
c_mid_top = cap_top + cap_hw + 4
c_mid_bot = cap_bot - cap_hw - 4
if c_mid_bot > c_mid_top:
    bd.rectangle([bx - cap_hw + 6, c_mid_top, bx - cap_hw + 11, c_mid_bot],
                 fill=(255, 255, 255, 48))

img = composite(img, bottle_l)

# -- outlines on top (non-transparent layer) --
od = ImageDraw.Draw(img)
oc = (200, 168, 118, 255)  # gold outline (opaque after composite)


pill_outline(od, bx, body_hw, body_top, body_bot, oc, 1)
pill_outline(od, bx, cap_hw,  cap_top,  cap_bot,  oc, 1)
od.rectangle([bx-neck_hw, neck_top, bx+neck_hw, neck_bot], outline=oc, width=1)
od.rectangle([bx-brush_hw, brush_top, bx+brush_hw, brush_bot], outline=oc, width=1)
# liquid level line
od.line([(bx - body_hw + 12, body_top + 95),
         (bx + body_hw - 12, body_top + 95)],
        fill=(210, 168, 118), width=1)

# ── LAYER 7: small secondary bottle (right, offset, slightly smaller) ─
b2_l, b2d = layer()
bx2 = 700
off = 0.72  # scale factor

def spill(hw, f): return int(hw * f)

b2_body_hw  = spill(body_hw,  off)
b2_body_top = body_top + 30
b2_body_bot = body_bot - 15
b2_neck_hw  = spill(neck_hw,  off)
b2_neck_top = b2_body_top - (neck_bot - neck_top)
b2_neck_bot = b2_body_top + 4
b2_cap_hw   = spill(cap_hw,   off)
b2_cap_top  = b2_neck_top - (cap_bot - cap_top)
b2_cap_bot  = b2_neck_top + 2
b2_brush_hw = 4
b2_brush_top = b2_cap_top - 42
b2_brush_bot = b2_cap_top + 2

# body fill - slightly different hue (blush)
pill_shape(b2d, bx2, b2_body_hw, b2_body_top, b2_body_bot, (*blush[:3], 148))
# liquid
liq2_top = b2_body_top + b2_body_hw + 38
if b2_body_bot - b2_body_hw - 8 > liq2_top:
    b2d.rectangle([bx2-b2_body_hw+8, liq2_top,
                   bx2+b2_body_hw-8, b2_body_bot-b2_body_hw-8],
                  fill=(200, 175, 210, 52))
# neck
if b2_neck_bot > b2_neck_top:
    b2d.rectangle([bx2-b2_neck_hw, b2_neck_top, bx2+b2_neck_hw, b2_neck_bot],
                  fill=(248, 242, 235, 182))
# cap
pill_shape(b2d, bx2, b2_cap_hw, b2_cap_top, b2_cap_bot, (*nude[:3], 162))
# brush
if b2_brush_bot > b2_brush_top:
    b2d.rectangle([bx2-b2_brush_hw, b2_brush_top, bx2+b2_brush_hw, b2_brush_bot],
                  fill=(*champagne[:3], 128))
b2d.ellipse([bx2-b2_brush_hw-1, b2_brush_top-10, bx2+b2_brush_hw+1, b2_brush_top],
            fill=(*champagne[:3], 118))
# highlight
b2_hl_mid_top = b2_body_top + b2_body_hw + 8
b2_hl_mid_bot = b2_body_bot - b2_body_hw - 10
if b2_hl_mid_bot > b2_hl_mid_top:
    b2d.rectangle([bx2-b2_body_hw+5, b2_hl_mid_top,
                   bx2-b2_body_hw+9, b2_hl_mid_bot],
                  fill=(255, 255, 255, 42))

img = composite(img, b2_l)
od2 = ImageDraw.Draw(img)
pill_outline(od2, bx2, b2_body_hw, b2_body_top, b2_body_bot, (200, 168, 118), 1)
pill_outline(od2, bx2, b2_cap_hw,  b2_cap_top,  b2_cap_bot,  (200, 168, 118), 1)
od2.rectangle([bx2-b2_neck_hw, b2_neck_top, bx2+b2_neck_hw, b2_neck_bot],
              outline=(200, 168, 118), width=1)

# ── TYPOGRAPHY ───────────────────────────────────────────
SERIF_REG  = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITAL = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_REG   = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

f_eyebrow = ImageFont.truetype(SANS_REG,  24)
f_title   = ImageFont.truetype(SERIF_ITAL, 132)
f_sub     = ImageFont.truetype(SERIF_REG,  54)
f_feat    = ImageFont.truetype(SANS_REG,   26)

td = ImageDraw.Draw(img)

def draw_centered(d, text, font, y, color, tracking=0):
    if tracking == 0:
        x = centered_x(d, text, font)
        d.text((x, y), text, fill=color, font=font)
    else:
        # manual letter-spacing
        total = 0
        chars = list(text)
        widths = []
        for ch in chars:
            bb = d.textbbox((0,0), ch, font=font)
            widths.append(bb[2] - bb[0])
            total += bb[2] - bb[0]
        total += tracking * (len(chars) - 1)
        x = (W - total) // 2
        for ch, cw in zip(chars, widths):
            d.text((x, y), ch, fill=color, font=font)
            x += cw + tracking

# Eyebrow
draw_centered(td, "G U M R O A D   T E M P L A T E",
              f_eyebrow, 466, (*light[:3],), tracking=0)

# Main title — "Nail Salon" in italic serif
draw_centered(td, "Nail Salon", f_title, 498, (*dark[:3],))

# Subtitle
draw_centered(td, "Website Template", f_sub, 665, (*medium[:3],))

# Thin gold divider
div_y = 758
div_len = 220
div_x1 = (W - div_len) // 2
td.line([(div_x1, div_y), (div_x1 + div_len, div_y)],
        fill=(*champagne[:3],), width=1)
# tiny diamonds on ends of line
for px in [div_x1, div_x1 + div_len]:
    td.polygon([(px, div_y-4), (px+4, div_y), (px, div_y+4), (px-4, div_y)],
               fill=(*gold[:3],))

# Feature line
draw_centered(td,
              "Elegant  ·  Responsive  ·  Easy to Edit  ·  No Coding",
              f_feat, 786, (*light[:3],))

# ── BORDER FRAME ─────────────────────────────────────────
m = 30
td.rectangle([m,   m,   W-m,   H-m],   outline=(*champagne[:3],), width=1)
td.rectangle([m+8, m+8, W-m-8, H-m-8], outline=(230, 205, 168),   width=1)

# ── FINAL EXPORT ─────────────────────────────────────────
out = img.convert("RGB")
out.save("/home/user/Game/gumroad-cover.jpg", "JPEG", quality=96, optimize=True)
out.save("/home/user/Game/gumroad-cover.png", "PNG",  optimize=True)
print("Saved: gumroad-cover.jpg + gumroad-cover.png")
print(f"Size: {out.size}")
