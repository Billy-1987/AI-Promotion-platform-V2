from PIL import Image, ImageDraw, ImageFont
import os

W = 1200
PAD = 56

WHITE  = (255, 255, 255)
DARK   = (28,  28,  40)
MID    = (90,  90, 110)
LIGHT  = (240, 240, 248)

# Header gradient
H_TOP = (80, 110, 230)
H_BOT = (130, 60, 180)

# Per-feature accent colours  (bg_light, accent, text_on_accent)
ACCENTS = [
    ((232, 240, 255), (80,  110, 230), WHITE),   # 1 blue-purple
    ((232, 255, 244), (22,  163, 100), WHITE),   # 2 green
    ((255, 237, 232), (220,  80,  50), WHITE),   # 3 coral
    ((255, 248, 225), (200, 140,   0), WHITE),   # 4 amber
    ((237, 232, 255), (120,  60, 200), WHITE),   # 5 violet
]

def load_font(size):
    for p in [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

F56 = load_font(56)
F40 = load_font(40)
F32 = load_font(32)
F26 = load_font(26)
F22 = load_font(22)
F18 = load_font(18)

def grad(draw, x1, y1, x2, y2, c1, c2):
    for i in range(y2 - y1):
        t = i / max(1, y2 - y1 - 1)
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        draw.line([(x1, y1+i), (x2, y1+i)], fill=c)

def rr(draw, x1, y1, x2, y2, r, fill, outline=None, ow=0):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)
    if outline:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, outline=outline, width=ow)

def tw(draw, text, font, max_w):
    lines, line = [], ''
    for ch in text:
        test = line + ch
        if draw.textbbox((0,0), test, font=font)[2] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = ch
    if line: lines.append(line)
    return lines

def lh(font):
    b = font.getbbox('国')
    return b[3] - b[1]

def draw_text_block(draw, lines, x, y, font, fill, spacing=6):
    h = lh(font)
    for l in lines:
        draw.text((x, y), l, font=font, fill=fill)
        y += h + spacing
    return y

def center_text(draw, text, font, y, fill, w=W):
    b = draw.textbbox((0,0), text, font=font)
    x = (w - (b[2]-b[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + lh(font)

# ── DATA ──────────────────────────────────────────────────────────────────────
FEATURES = [
    {
        "num": "01",
        "title": "运营日历",
        "tagline": "推广重点，进平台即知",
        "pain": "以往：翻邮件 → 找附件 → 对日期，信息滞后还易遗漏",
        "bullets": [
            ("商品部日历直连平台", "自动同步，无需手动转发"),
            ("节点 / 主题 / 素材一屏呈现", "推广重点一目了然"),
            ("支持订阅提醒", "关键节点提前预警"),
        ],
        "stat_num": "80%",
        "stat_label": "信息查找时间节省",
    },
    {
        "num": "02",
        "title": "模板社区",
        "tagline": "全年节点模板，随取随用",
        "pain": "以往：东拼西凑找素材，版权不清，风格不统一",
        "bullets": [
            ("覆盖全年节日 / 节气 / 促销日", "AI 生成，100% 无版权风险"),
            ("按日历节点智能推荐", "打开即是当季模板"),
            ("一键套用品牌风格", "10 分钟出图"),
        ],
        "stat_num": "2天→10分",
        "stat_label": "素材准备时间",
    },
    {
        "num": "03",
        "title": "AI 换装",
        "tagline": "实拍图秒变社群推广图",
        "pain": "以往：找修图师 → 沟通需求 → 等待交付，一张图 50 元起",
        "bullets": [
            ("实拍图 / 白底图 / 上身图均可上传", "AI 一键智能换装"),
            ("随意切换场景与画面风格", "无需重拍"),
            ("一键打 BIGOFFS logo", "品牌感即刻到位"),
        ],
        "stat_num": "¥50→¥0",
        "stat_label": "单张修图成本",
    },
    {
        "num": "04",
        "title": "AI 图片设计",
        "tagline": "输入提示词，AI 直接出图",
        "pain": "以往：提需求 → 等排期 → 反复改稿，最快也要 2 天",
        "bullets": [
            ("自然语言描述即可生成图片", "无需任何设计技能"),
            ("多风格版本同时输出", "秒级对比选择"),
            ("无限次修改，零沟通成本", "想改就改"),
        ],
        "stat_num": "2天→1分",
        "stat_label": "设计需求响应时间",
    },
    {
        "num": "05",
        "title": "我的图库",
        "tagline": "所有推广图，统一管理",
        "pain": "以往：图片散落微信 / 邮件 / 本地，找图靠记忆",
        "bullets": [
            ("所有生成 & 上传图片集中归档", "告别文件夹混乱"),
            ("一键打标 / 批量下载", "常用操作零摩擦"),
            ("团队共享，实时同步", "协作无障碍"),
        ],
        "stat_num": "10×",
        "stat_label": "素材管理效率提升",
    },
]

# ── MEASURE ───────────────────────────────────────────────────────────────────
dummy = Image.new("RGB", (W, 100), WHITE)
dd = ImageDraw.Draw(dummy)

CARD_PAD = 44
INNER_W  = W - PAD*2 - CARD_PAD*2

def measure_card(feat):
    # tagline
    h = lh(F32) + 10
    # pain strip
    pain_lines = tw(dd, feat["pain"], F22, INNER_W - 20)
    h += 16 + len(pain_lines) * (lh(F22)+6) + 16
    # bullets: 3 rows, each ~2 lines
    for left, right in feat["bullets"]:
        ll = tw(dd, left,  F26, (INNER_W-40)//2 - 10)
        rl = tw(dd, right, F22, (INNER_W-40)//2 - 10)
        row_h = max(len(ll)*(lh(F26)+4), len(rl)*(lh(F22)+4))
        h += row_h + 20
    # stat bar
    h += 80
    return CARD_PAD*2 + lh(F40) + 14 + h + 20

HEADER_H = 220
DIVIDER_H = 4
GAP = 24
FOOTER_H = 200

card_heights = [measure_card(f) for f in FEATURES]
TOTAL_H = HEADER_H + sum(card_heights) + GAP*(len(FEATURES)+1) + FOOTER_H + 60

# ── DRAW ──────────────────────────────────────────────────────────────────────
img  = Image.new("RGB", (W, TOTAL_H), (245, 245, 252))
draw = ImageDraw.Draw(img)

# full background
grad(draw, 0, 0, W, TOTAL_H, (245,245,252), (230,228,248))

# ── HEADER ────────────────────────────────────────────────────────────────────
grad(draw, 0, 0, W, HEADER_H, H_TOP, H_BOT)

cy = 44
cy = center_text(draw, "BIGOFFS 智能推广平台 (AIPP)", F56, cy, WHITE)
cy += 14
cy = center_text(draw, "五大核心功能  ·  让推广更简单", F26, cy, (210, 210, 255))
cy += 12
cy = center_text(draw, "运营日历  /  模板社区  /  AI换装  /  AI图片设计  /  我的图库", F22, cy, (180, 180, 240))

# ── FEATURE CARDS ─────────────────────────────────────────────────────────────
cy = HEADER_H + GAP

for idx, feat in enumerate(FEATURES):
    bg_light, accent, _ = ACCENTS[idx]
    card_h = card_heights[idx]
    cx = PAD

    # card shadow (offset rect)
    rr(draw, cx+4, cy+4, cx+W-PAD*2+4, cy+card_h+4, 16, (200,198,220))
    # card body
    rr(draw, cx, cy, cx+W-PAD*2, cy+card_h, 16, WHITE)
    # top accent strip
    rr(draw, cx, cy, cx+W-PAD*2, cy+6, 16, accent)
    draw.rectangle([cx, cy+3, cx+W-PAD*2, cy+6], fill=accent)

    ix = cx + CARD_PAD
    iy = cy + CARD_PAD

    # ── number + title row ──
    # number pill
    num_text = feat["num"]
    nb = draw.textbbox((0,0), num_text, font=F40)
    pill_w = (nb[2]-nb[0]) + 28
    pill_h = lh(F40) + 10
    rr(draw, ix, iy, ix+pill_w, iy+pill_h, pill_h//2, accent)
    draw.text((ix+14, iy+4), num_text, font=F40, fill=WHITE)

    # title
    title_x = ix + pill_w + 20
    draw.text((title_x, iy+2), feat["title"], font=F40, fill=DARK)
    iy += pill_h + 14

    # tagline
    draw.text((ix, iy), feat["tagline"], font=F32, fill=accent)
    iy += lh(F32) + 10

    # pain strip
    pain_lines = tw(draw, feat["pain"], F22, INNER_W - 20)
    strip_h = len(pain_lines) * (lh(F22)+6) + 16
    rr(draw, ix, iy, ix+INNER_W, iy+strip_h, 8, (255,248,235))
    draw.rectangle([ix, iy+4, ix+4, iy+strip_h-4], fill=(255,180,0))
    piy = iy + 8
    for line in pain_lines:
        draw.text((ix+14, piy), line, font=F22, fill=(140,100,0))
        piy += lh(F22)+6
    iy += strip_h + 18

    # bullets
    col_w = (INNER_W - 40) // 2
    for left, right in feat["bullets"]:
        ll = tw(draw, left,  F26, col_w - 10)
        rl = tw(draw, right, F22, col_w - 10)
        row_h = max(len(ll)*(lh(F26)+4), len(rl)*(lh(F22)+4)) + 4

        # left: bold feature text
        biy = iy
        for line in ll:
            draw.text((ix, biy), line, font=F26, fill=DARK)
            biy += lh(F26)+4

        # arrow
        arr_x = ix + col_w + 4
        arr_y = iy + row_h//2 - lh(F26)//2
        draw.text((arr_x, arr_y), "→", font=F26, fill=accent)

        # right: benefit text
        biy2 = iy
        for line in rl:
            draw.text((ix + col_w + 36, biy2), line, font=F22, fill=MID)
            biy2 += lh(F22)+4

        iy += row_h + 20

    # stat bar
    stat_bg = bg_light
    rr(draw, ix, iy, ix+INNER_W, iy+68, 10, stat_bg)
    # big number
    sn = feat["stat_num"]
    sb = draw.textbbox((0,0), sn, font=F40)
    draw.text((ix+24, iy+10), sn, font=F40, fill=accent)
    sl_x = ix + 24 + (sb[2]-sb[0]) + 16
    draw.text((sl_x, iy+22), feat["stat_label"], font=F22, fill=MID)
    iy += 68

    cy += card_h + GAP

# ── FOOTER ────────────────────────────────────────────────────────────────────
cy += GAP
grad(draw, 0, cy, W, cy+FOOTER_H, H_BOT, H_TOP)

# three stats
stats = [("效率提升 10×", "推广全流程自动化"), ("成本降低 70%", "减少人工与外包投入"), ("零门槛上手", "无需设计 / 技术背景")]
sw = (W - PAD*2 - 40) // 3
for i, (big, small) in enumerate(stats):
    sx = PAD + i*(sw+20)
    sy = cy + 30
    rr(draw, sx, sy, sx+sw, sy+120, 12, (255,255,255,30))
    draw.rounded_rectangle([sx, sy, sx+sw, sy+120], radius=12, outline=(255,255,255), width=1)
    bb = draw.textbbox((0,0), big, font=F32)
    draw.text((sx+(sw-(bb[2]-bb[0]))//2, sy+16), big, font=F32, fill=WHITE)
    bs = draw.textbbox((0,0), small, font=F22)
    draw.text((sx+(sw-(bs[2]-bs[0]))//2, sy+62), small, font=F22, fill=(210,210,255))

tagline = "让每一位推广同学都拥有 AI 助手"
tb = draw.textbbox((0,0), tagline, font=F26)
draw.text(((W-(tb[2]-tb[0]))//2, cy+FOOTER_H-54), tagline, font=F26, fill=(220,220,255))

# ── SAVE ──────────────────────────────────────────────────────────────────────
out = "/Users/ai06/Desktop/智能推广平台AIPP/aipp-poster.jpg"
img.save(out, "JPEG", quality=96)
print(f"Saved {out}  {W}×{TOTAL_H}px")
