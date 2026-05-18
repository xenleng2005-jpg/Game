"""
Generates a 1200x1200 website-preview thumbnail for Gumroad.
Looks like a clean screenshot of the nail-salon template's hero section.
"""
from PIL import Image, ImageDraw, ImageFont
import math

W = H = 1200
img = Image.new("RGBA", (W, H), (250, 248, 245, 255))

# ── palette ──────────────────────────────────────────────
def c(r,g,b,a=255): return (r,g,b,a)
nude      = c(240,224,214)
blush     = c(232,196,184)
champagne = c(212,175,122)
gold      = c(201,169,110)
dark      = c(58, 50, 40)
medium    = c(107,91, 78)
light     = c(156,136,128)
cream     = c(245,240,235)

SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_R  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def layer():
    l = Image.new("RGBA", (W, H), (0,0,0,0))
    return l, ImageDraw.Draw(l)

def comp(base, over):
    return Image.alpha_composite(base, over)

def pill_shape(d, cx, hw, top, bot, fill):
    d.ellipse([cx-hw, top, cx+hw, top+hw*2], fill=fill)
    mt, mb = top+hw, bot-hw
    if mb > mt: d.rectangle([cx-hw, mt, cx+hw, mb], fill=fill)
    d.ellipse([cx-hw, bot-hw*2, cx+hw, bot], fill=fill)

def pill_outline(d, cx, hw, top, bot, col, w=1):
    d.arc([cx-hw, top, cx+hw, top+hw*2], 180, 0, fill=col, width=w)
    mt, mb = top+hw, bot-hw
    if mb > mt:
        d.line([(cx-hw, mt),(cx-hw, mb)], fill=col, width=w)
        d.line([(cx+hw, mt),(cx+hw, mb)], fill=col, width=w)
    d.arc([cx-hw, bot-hw*2, cx+hw, bot], 0, 180, fill=col, width=w)

def draw_sparkle(d, cx, cy, size, col):
    d.line([(cx,cy-size),(cx,cy+size)], fill=col, width=1)
    d.line([(cx-size,cy),(cx+size,cy)], fill=col, width=1)
    s = int(size*0.65)
    d.line([(cx-s,cy-s),(cx+s,cy+s)], fill=col, width=1)
    d.line([(cx+s,cy-s),(cx-s,cy+s)], fill=col, width=1)

def arc_pts(cx,cy,rx,ry,a0,a1,n=100):
    return [(cx+rx*math.cos(math.radians(a0+(a1-a0)*i/n)),
             cy+ry*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

def draw_curve(d, pts, col, width=1):
    for i in range(len(pts)-1): d.line([pts[i],pts[i+1]], fill=col, width=width)

NAV_H = 62   # navigation bar height

# ════════════════════════════════════════════════════════
# LAYER 1 — background gradient (hero area only, below nav)
# ════════════════════════════════════════════════════════
bg, bgd = layer()
for y in range(NAV_H, H):
    t = (y - NAV_H) / (H - NAV_H)
    r = int(250*(1-t) + 237*t)
    g = int(248*(1-t) + 221*t)
    b = int(245*(1-t) + 213*t)
    bgd.line([(0,y),(W,y)], fill=(r,g,b,255))
img = comp(img, bg)

# ════════════════════════════════════════════════════════
# LAYER 2 — ambient circle glow (hero bg decoration)
# ════════════════════════════════════════════════════════
gl, gld = layer()
gld.ellipse([700,-60,1300,540],  fill=(*blush[:3], 36))
gld.ellipse([740, 0, 1260,480],  fill=(*nude[:3],  26))
gld.ellipse([-80, 700,380,1160], fill=(*nude[:3],  30))
gld.ellipse([-40, 750,340,1120], fill=(*blush[:3], 22))
img = comp(img, gl)

# ════════════════════════════════════════════════════════
# LAYER 3 — thin arc decorations
# ════════════════════════════════════════════════════════
al, ald = layer()
ac = (*champagne[:3], 16)
draw_curve(ald, arc_pts(300,500,340,380,-170,-10), ac)
draw_curve(ald, arc_pts(300,750,340,380,  10, 170), ac)
img = comp(img, al)

# ════════════════════════════════════════════════════════
# LAYER 4 — scattered gold dots
# ════════════════════════════════════════════════════════
dl, dd = layer()
for (x,y,r,a) in [
    (135,170,3,68),(960,230,3,60),(120,700,3,55),(1060,620,3.5,62),
    (200,1020,3,58),(1040,980,3,52),(80,430,2.5,44),(1100,420,2.5,44),
    (360,140,3,64),(880,145,2.5,54),(105,1120,2.5,48),(1095,1110,2.5,48),
]:
    r=int(r); dd.ellipse([x-r,y-r,x+r,y+r], fill=(*champagne[:3],a))
img = comp(img, dl)

# ════════════════════════════════════════════════════════
# LAYER 5 — sparkles
# ════════════════════════════════════════════════════════
sl, sd = layer()
sc = (*gold[:3], 125)
draw_sparkle(sd, 135, 410, 13, sc)
draw_sparkle(sd, 490, 310, 10, sc)
draw_sparkle(sd, 118, 630,  8, (*champagne[:3], 105))
draw_sparkle(sd, 515, 840,  8, (*champagne[:3], 100))
for (x,y,r) in [(500,480,3),(480,680,3),(168,900,3),(158,260,3)]:
    sd.ellipse([x-r,y-r,x+r,y+r], fill=(*gold[:3], 115))
img = comp(img, sl)

# ════════════════════════════════════════════════════════
# LAYER 6 — nail bottle illustration (left side)
# All centered around bx=310
# ════════════════════════════════════════════════════════
bx = 310

body_hw, body_top, body_bot = 68,  220, 520
neck_hw, neck_top, neck_bot = 24,  164, 224
cap_hw,  cap_top,  cap_bot  = 26,  114, 170
brush_hw,brush_top,brush_bot = 6,   58, 118

bl, bd2 = layer()

pill_shape(bd2, bx, body_hw, body_top, body_bot, (*nude[:3], 215))
liq_top = body_top + 115
pill_shape(bd2, bx, body_hw-14, liq_top, body_bot-12, (224,152,152,52))
bd2.ellipse([bx-body_hw, neck_bot-12, bx+body_hw, neck_bot+12],
            fill=(*blush[:3], 68))
bd2.rectangle([bx-neck_hw, neck_top, bx+neck_hw, neck_bot],
              fill=(248,242,235,228))
pill_shape(bd2, bx, cap_hw, cap_top, cap_bot, (*champagne[:3], 180))
bd2.rectangle([bx-brush_hw, brush_top, bx+brush_hw, brush_bot],
              fill=(*gold[:3], 162))
bd2.ellipse([bx-brush_hw-2, brush_top-16, bx+brush_hw+2, brush_top+2],
            fill=(*gold[:3], 148))
# highlights
mt = body_top+body_hw+12; mb = body_bot-body_hw-18
if mb>mt: bd2.rectangle([bx-body_hw+8, mt, bx-body_hw+14, mb], fill=(255,255,255,55))
cmt=cap_top+cap_hw+5; cmb=cap_bot-cap_hw-5
if cmb>cmt: bd2.rectangle([bx-cap_hw+7, cmt, bx-cap_hw+12, cmb], fill=(255,255,255,50))

img = comp(img, bl)

# outlines
od = ImageDraw.Draw(img)
oc = (200,168,118)
pill_outline(od, bx, body_hw, body_top, body_bot, oc, 1)
pill_outline(od, bx, cap_hw,  cap_top,  cap_bot,  oc, 1)
od.rectangle([bx-neck_hw, neck_top, bx+neck_hw, neck_bot], outline=oc, width=1)
od.rectangle([bx-brush_hw, brush_top, bx+brush_hw, brush_bot], outline=oc, width=1)
od.line([(bx-body_hw+14, liq_top),(bx+body_hw-14, liq_top)], fill=(210,178,130), width=1)

# ── secondary smaller bottle (right of main, slightly behind)
bx2, off = 428, 0.68
b2 = {
    "body_hw": int(body_hw*off), "body_top": body_top+38, "body_bot": body_bot-18,
    "neck_hw": int(neck_hw*off),
    "cap_hw":  int(cap_hw*off),
    "brush_hw": 5,
}
b2["neck_top"] = b2["body_top"] - (neck_bot-neck_top)
b2["neck_bot"] = b2["body_top"] + 5
b2["cap_top"]  = b2["neck_top"] - (cap_bot-cap_top)
b2["cap_bot"]  = b2["neck_top"] + 3
b2["brush_top"]= b2["cap_top"] - 44
b2["brush_bot"]= b2["cap_top"] + 3

b2l, b2d = layer()
pill_shape(b2d, bx2, b2["body_hw"], b2["body_top"], b2["body_bot"], (*blush[:3], 148))
liq2t = b2["body_top"]+b2["body_hw"]+42
if b2["body_bot"]-b2["body_hw"]-8 > liq2t:
    b2d.rectangle([bx2-b2["body_hw"]+8, liq2t,
                   bx2+b2["body_hw"]-8, b2["body_bot"]-b2["body_hw"]-8],
                  fill=(200,175,210,50))
if b2["neck_bot"] > b2["neck_top"]:
    b2d.rectangle([bx2-b2["neck_hw"], b2["neck_top"],
                   bx2+b2["neck_hw"], b2["neck_bot"]], fill=(248,242,235,180))
pill_shape(b2d, bx2, b2["cap_hw"], b2["cap_top"], b2["cap_bot"], (*nude[:3], 158))
if b2["brush_bot"] > b2["brush_top"]:
    b2d.rectangle([bx2-b2["brush_hw"], b2["brush_top"],
                   bx2+b2["brush_hw"], b2["brush_bot"]], fill=(*champagne[:3], 128))
b2d.ellipse([bx2-b2["brush_hw"]-1, b2["brush_top"]-11,
             bx2+b2["brush_hw"]+1, b2["brush_top"]], fill=(*champagne[:3], 118))
# highlight
bm_t = b2["body_top"]+b2["body_hw"]+10; bm_b = b2["body_bot"]-b2["body_hw"]-12
if bm_b > bm_t:
    b2d.rectangle([bx2-b2["body_hw"]+5, bm_t, bx2-b2["body_hw"]+9, bm_b],
                  fill=(255,255,255,42))
img = comp(img, b2l)
od3 = ImageDraw.Draw(img)
pill_outline(od3, bx2, b2["body_hw"], b2["body_top"], b2["body_bot"], (200,168,118), 1)
pill_outline(od3, bx2, b2["cap_hw"],  b2["cap_top"],  b2["cap_bot"],  (200,168,118), 1)

# ════════════════════════════════════════════════════════
# TEXT — right side of hero (x center ~820)
# ════════════════════════════════════════════════════════
td = ImageDraw.Draw(img)

f_eyebrow  = ImageFont.truetype(SANS_R,  22)
f_title_lg = ImageFont.truetype(SERIF_I, 108)
f_subtitle = ImageFont.truetype(SERIF_R,  40)
f_small    = ImageFont.truetype(SANS_R,   24)
f_btn      = ImageFont.truetype(SANS_R,   22)
f_badge    = ImageFont.truetype(SANS_R,   20)

# right column bounding box: x=590 to x=1160, center x=875
TX = 875

def tw(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]

def draw_right(d, text, font, y, color, align="center"):
    w, _ = tw(d, text, font)
    if align == "center":
        x = TX - w//2
    else:  # left from TX-280
        x = 590
    d.text((x, y), text, fill=color, font=font)

# Eyebrow
ey_text = "WELCOME  TO  YOUR  SALON  NAME"
ew, _ = tw(td, ey_text, f_eyebrow)
td.text((TX - ew//2, 178), ey_text, fill=(*gold[:3],), font=f_eyebrow)

# Title line 1 — "Beautiful Nails,"
t1 = "Beautiful Nails,"
t1w, t1h = tw(td, t1, f_title_lg)
td.text((TX - t1w//2, 228), t1, fill=(*dark[:3],), font=f_title_lg)

# Title line 2 — "Beautiful You" (italic, gold)
t2 = "Beautiful You"
t2w, _ = tw(td, t2, f_title_lg)
td.text((TX - t2w//2, 348), t2, fill=(*gold[:3],), font=f_title_lg)

# Subtitle
sub = "Expert nail care crafted with"
sub2 = "precision and passion."
sw, _ = tw(td, sub, f_subtitle)
td.text((TX - sw//2, 492), sub,  fill=(*medium[:3],), font=f_subtitle)
sw2, _ = tw(td, sub2, f_subtitle)
td.text((TX - sw2//2, 538), sub2, fill=(*medium[:3],), font=f_subtitle)

# Trust badges
badges = ["✓ Premium Products", "✓ Certified Technicians", "✓ Walk-ins Welcome"]
by = 620
for badge in badges:
    bw, _ = tw(td, badge, f_badge)
    td.text((TX - bw//2, by), badge, fill=(*medium[:3],), font=f_badge)
    by += 34

# Book Now button
btn_text = "BOOK  NOW"
btn_w, btn_h = tw(td, btn_text, f_btn)
pad_x, pad_y = 44, 18
btn_rect_w = btn_w + pad_x*2
btn_rect_h = btn_h + pad_y*2
bx_left = TX - btn_rect_w//2
bx_right = bx_left + btn_rect_w
btn_top = 754
btn_bot = btn_top + btn_rect_h

td.rectangle([bx_left, btn_top, bx_right, btn_bot], fill=(*dark[:3],))
td.text((bx_left + pad_x, btn_top + pad_y), btn_text,
        fill=(250,248,245), font=f_btn)

# ════════════════════════════════════════════════════════
# NAVIGATION BAR
# ════════════════════════════════════════════════════════
nav_l, nav_d = layer()
# Cream background with bottom border
nav_d.rectangle([0, 0, W, NAV_H], fill=(250,248,245,252))
nav_d.line([(0, NAV_H-1),(W, NAV_H-1)], fill=(*champagne[:3], 55), width=1)

# Logo placeholder (dashed border)
logo_text = "YOUR LOGO"
f_logo = ImageFont.truetype(SERIF_R, 20)
lw, lh = nav_d.textbbox((0,0), logo_text, font=f_logo)[2:4]
lw = nav_d.textbbox((0,0), logo_text, font=f_logo)[2]
lx, ly = 60, (NAV_H - lh) // 2 - 2
logo_pad = 10
nav_d.rectangle([lx-logo_pad, ly-6, lx+lw+logo_pad, ly+lh+4],
                outline=(*champagne[:3], 140), width=1)
# dashed effect — PIL can't do dashed natively, use dotted approximation
for x in range(lx-logo_pad, lx+lw+logo_pad, 8):
    nav_d.point((x, ly-6), fill=(*champagne[:3], 140))
    nav_d.point((x, ly+lh+4), fill=(*champagne[:3], 140))
for y in range(ly-6, ly+lh+4, 8):
    nav_d.point((lx-logo_pad, y), fill=(*champagne[:3], 140))
    nav_d.point((lx+lw+logo_pad, y), fill=(*champagne[:3], 140))
nav_d.text((lx, ly), logo_text, fill=(*dark[:3],), font=f_logo)

# Nav items
f_nav = ImageFont.truetype(SANS_R, 17)
nav_items = ["Home", "Services", "Gallery", "About", "Contact"]
nav_col = (*medium[:3],)
nx = W - 80
for item in reversed(nav_items):
    iw = nav_d.textbbox((0,0), item, font=f_nav)[2]
    iy = (NAV_H - 17) // 2
    nav_d.text((nx - iw, iy), item, fill=nav_col, font=f_nav)
    nx -= iw + 34

img = comp(img, nav_l)

# ════════════════════════════════════════════════════════
# BOTTOM SERVICES STRIP PEEK
# ════════════════════════════════════════════════════════
strip_top = 920
strip_l, strip_d = layer()

# Cream background strip
strip_d.rectangle([0, strip_top, W, H], fill=(245,240,235,255))

# Section heading
f_sec_eye = ImageFont.truetype(SANS_R, 18)
f_sec_ttl = ImageFont.truetype(SERIF_I, 52)
sey = "OUR SERVICES"
sew = strip_d.textbbox((0,0), sey, font=f_sec_eye)[2]
strip_d.text(((W-sew)//2, strip_top+20), sey, fill=(*gold[:3],), font=f_sec_eye)
st = "Crafted to Perfection"
stw = strip_d.textbbox((0,0), st, font=f_sec_ttl)[2]
strip_d.text(((W-stw)//2, strip_top+48), st, fill=(*dark[:3],), font=f_sec_ttl)

# Thin divider
strip_d.line([(W//2-24, strip_top+108),(W//2+24, strip_top+108)],
             fill=(*champagne[:3],), width=1)

# Three service cards peek
card_names = ["Classic Manicure", "Gel Polish", "Acrylic Full Set", "Pedicure", "Nail Art"]
card_prices= ["$25", "$35", "$50", "$40", "$15+"]
card_w = 196
card_gap = 18
total_cw  = len(card_names)*card_w + (len(card_names)-1)*card_gap
cx_start  = (W - total_cw)//2

f_cname  = ImageFont.truetype(SERIF_R, 22)
f_cprice = ImageFont.truetype(SERIF_I, 32)
f_cnote  = ImageFont.truetype(SANS_R,  14)

card_top = strip_top + 128
card_bot = H - 30

for i, (name, price) in enumerate(zip(card_names, card_prices)):
    cx1 = cx_start + i*(card_w+card_gap)
    cx2 = cx1 + card_w
    strip_d.rectangle([cx1, card_top, cx2, card_bot],
                      fill=(255,255,255,255))
    strip_d.rectangle([cx1, card_top, cx2, card_bot],
                      outline=(*champagne[:3], 55), width=1)
    # card content centered
    ccx = (cx1+cx2)//2
    nw = strip_d.textbbox((0,0), name, font=f_cname)[2]
    strip_d.text((ccx-nw//2, card_top+22), name, fill=(*dark[:3],), font=f_cname)
    pw = strip_d.textbbox((0,0), price, font=f_cprice)[2]
    strip_d.text((ccx-pw//2, card_top+56), price, fill=(*gold[:3],), font=f_cprice)
    note = "from"
    now = strip_d.textbbox((0,0), note, font=f_cnote)[2]
    strip_d.text((ccx-now//2, card_top+94), note, fill=(*light[:3],), font=f_cnote)

img = comp(img, strip_l)

# ════════════════════════════════════════════════════════
# OUTER FRAME (thin gold double border)
# ════════════════════════════════════════════════════════
fd = ImageDraw.Draw(img)
m = 0  # no outer margin — full bleed
fd.rectangle([m, m, W-1-m, H-1-m], outline=(*champagne[:3],), width=1)

# ════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════
out = img.convert("RGB")
out.save("/home/user/Game/gumroad-thumbnail.png", "PNG",  optimize=True)
out.save("/home/user/Game/gumroad-thumbnail.jpg", "JPEG", quality=97, optimize=True)
print(f"Done — {out.size[0]}x{out.size[1]}px")
print("Saved: gumroad-thumbnail.png / .jpg")
