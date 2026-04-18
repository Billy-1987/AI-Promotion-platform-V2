from PIL import Image, ImageDraw, ImageFont
import os

W = 1200
PADDING = 60
BG_TOP = (102, 126, 234)
BG_BOT = (118, 75, 162)
WHITE = (255, 255, 255)
GRAY_BG = (248, 249, 250)
GRAY_TEXT = (100, 100, 100)
DARK = (40, 40, 40)
PURPLE = (102, 126, 234)
YELLOW_BG = (255, 243, 205)
YELLOW_BORDER = (255, 193, 7)
YELLOW_TEXT = (133, 100, 4)
GREEN_BG = (212, 237, 218)
GREEN_BORDER = (40, 167, 69)
GREEN_TEXT = (21, 87, 36)
BLUE_BG = (227, 242, 253)
BLUE_BORDER = (33, 150, 243)
BLUE_TEXT = (13, 71, 161)
RED_MARK = (220, 53, 69)

def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode MS.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def gradient_rect(draw, x1, y1, x2, y2, c1, c2, vertical=True):
    if vertical:
        for i in range(y2 - y1):
            t = i / max(1, y2 - y1 - 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            draw.line([(x1, y1 + i), (x2, y1 + i)], fill=(r, g, b))
    else:
        for i in range(x2 - x1):
            t = i / max(1, x2 - x1 - 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            draw.line([(x1 + i, y1), (x1 + i, y2)], fill=(r, g, b))

def rounded_rect(draw, x1, y1, x2, y2, r, fill, border=None, border_width=0):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)
    if border:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, outline=border, width=border_width)

def wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split('\n'):
        words = list(paragraph)
        line = ''
        for ch in words:
            test = line + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = ch
        if line:
            lines.append(line)
    return lines

def text_height(lines, font, line_spacing=8):
    if not lines:
        return 0
    sample = lines[0]
    h = font.getbbox(sample)[3] - font.getbbox(sample)[1] if hasattr(font, 'getbbox') else 20
    return len(lines) * (h + line_spacing)

def draw_multiline(draw, lines, x, y, font, fill, line_spacing=8, center_w=None):
    cy = y
    for line in lines:
        if center_w:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((x + (center_w - lw) // 2, cy), line, font=font, fill=fill)
        else:
            draw.text((x, cy), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1]
        cy += lh + line_spacing
    return cy

# ── fonts ──────────────────────────────────────────────────────────────────
f_title_big  = load_font(52, bold=True)
f_title_med  = load_font(36, bold=True)
f_title_sm   = load_font(28, bold=True)
f_body       = load_font(22)
f_body_sm    = load_font(19)
f_label      = load_font(24, bold=True)
f_num        = load_font(38, bold=True)
f_sub        = load_font(26)

# ── pre-calculate total height ─────────────────────────────────────────────
FEATURES = [
    {
        "num": "1",
        "icon": "📅",
        "title": "运营日历",
        "desc": "完美对接商品部定期输出的运营日历，门店小推手无需进入邮箱打开邮件查询，进入平台即可清晰查看推广重点",
        "pains": ["邮件查找繁琐，效率低下", "信息分散，容易遗漏重要节点", "无法快速定位推广重点", "跨部门信息同步困难"],
        "solutions": ["一键查看所有运营日历", "推广重点一目了然", "自动同步商品部更新", "支持日历订阅和提醒"],
        "value": "门店推广人员节省 80% 的信息查找时间，推广计划执行效率提升 3 倍",
    },
    {
        "num": "2",
        "icon": "🎨",
        "title": "模板社区",
        "desc": "各个节日、节气、促销日，推广同学无需到处找模板，且 AI 生成的模板无版权风险",
        "pains": ["模板资源分散难以查找", "版权风险难以把控", "模板质量参差不齐", "节日素材准备不及时"],
        "solutions": ["海量 AI 生成模板库", "100% 无版权风险", "按节日/节气智能分类", "一键套用快速出图"],
        "value": "覆盖全年所有营销节点，推广素材准备时间从 2 天缩短至 10 分钟，零版权风险",
    },
    {
        "num": "3",
        "icon": "👗",
        "title": "AI 换装",
        "desc": "可将上传的实拍图、白底图、上身图一键换装，随意改变画面风格，并可「一键打 BIGOFFS logo」，帮助推广同学轻松拿捏社群推广",
        "pains": ["专业修图成本高昂", "场景拍摄耗时费力", "风格调整需要重拍", "品牌 logo 添加繁琐"],
        "solutions": ["AI 一键智能换装", "多种风格随意切换", "自动添加品牌 logo", "秒级生成专业效果"],
        "value": "单张图片处理成本从 50 元降至 0 元，处理时间从 30 分钟缩短至 10 秒，素材产出效率提升 100 倍",
    },
    {
        "num": "4",
        "icon": "🖼",
        "title": "AI 图片设计",
        "desc": "运营同学仅输入提示词，AI 即可输出相应图片，无需任何专业设计技能",
        "pains": ["依赖专业设计师资源", "设计周期长影响效率", "沟通成本高易出错", "修改迭代耗时费力"],
        "solutions": ["文字描述即可生成图片", "秒级输出专业设计", "无限次修改零成本", "多版本快速对比选择"],
        "value": "运营人员无需设计技能即可独立完成图片创作，设计需求响应时间从 2 天缩短至 1 分钟",
    },
    {
        "num": "5",
        "icon": "📚",
        "title": "我的图库",
        "desc": "轻松管理所有操作过的图片内容，支持图片一键下载、一键打标等常用功能",
        "pains": ["素材散落各处难管理", "查找历史素材费时", "团队协作共享困难", "素材分类整理繁琐"],
        "solutions": ["集中管理所有素材", "智能标签快速检索", "一键批量下载导出", "团队共享实时同步"],
        "value": "素材管理效率提升 10 倍，查找时间从 10 分钟缩短至 10 秒，团队协作效率提升 5 倍",
    },
]

# ── draw ───────────────────────────────────────────────────────────────────
# First pass: measure heights
def measure_feature_card(feat, draw):
    inner_w = W - PADDING * 2 - 40  # card inner width (minus left bar + padding)
    text_w = inner_w - 40

    # title row: 80px
    title_h = 80
    # desc
    desc_lines = wrap_text(feat["desc"], f_body, text_w - 20, draw)
    desc_h = text_height(desc_lines, f_body, 10) + 20
    # pain/solution boxes side by side
    col_w = (text_w - 20) // 2
    pain_lines = [wrap_text(p, f_body_sm, col_w - 50, draw) for p in feat["pains"]]
    sol_lines  = [wrap_text(s, f_body_sm, col_w - 50, draw) for s in feat["solutions"]]
    box_h = 40  # header
    for pl, sl in zip(pain_lines, sol_lines):
        lh = max(text_height(pl, f_body_sm, 6), text_height(sl, f_body_sm, 6))
        box_h += lh + 14
    box_h += 20
    # value box
    val_lines = wrap_text(feat["value"], f_body, text_w - 20, draw)
    val_h = text_height(val_lines, f_body, 10) + 50
    return 30 + title_h + desc_h + 20 + box_h + 20 + val_h + 30

# Dummy image for measuring
dummy = Image.new("RGB", (W, 100), WHITE)
dummy_draw = ImageDraw.Draw(dummy)

HEADER_H = 260
FOOTER_H = 280
GAP = 30

card_heights = [measure_feature_card(f, dummy_draw) for f in FEATURES]
total_h = HEADER_H + sum(card_heights) + GAP * (len(FEATURES) + 1) + FOOTER_H + 60

img = Image.new("RGB", (W, total_h), WHITE)
draw = ImageDraw.Draw(img)

# ── background gradient ────────────────────────────────────────────────────
gradient_rect(draw, 0, 0, W, total_h, BG_TOP, BG_BOT)

# ── HEADER ─────────────────────────────────────────────────────────────────
cy = 50
# Main title
title = "BIGOFFS 智能推广平台"
bbox = draw.textbbox((0, 0), title, font=f_title_big)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, cy), title, font=f_title_big, fill=WHITE)
cy += bbox[3] - bbox[1] + 18

sub = "AI 驱动的全链路营销自动化解决方案"
bbox = draw.textbbox((0, 0), sub, font=f_sub)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, cy), sub, font=f_sub, fill=(220, 220, 255))
cy += bbox[3] - bbox[1] + 14

tag = "让推广更简单，让营销更智能"
bbox = draw.textbbox((0, 0), tag, font=f_body)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, cy), tag, font=f_body, fill=(200, 200, 240))
cy += bbox[3] - bbox[1] + 30

# ── FEATURE CARDS ──────────────────────────────────────────────────────────
for feat in FEATURES:
    cy += GAP
    card_h = measure_feature_card(feat, draw)
    cx = PADDING

    # Card background
    rounded_rect(draw, cx, cy, cx + W - PADDING * 2, cy + card_h, 16, WHITE)
    # Left accent bar
    rounded_rect(draw, cx, cy, cx + 8, cy + card_h, 4,
                 (int(BG_TOP[0] + (BG_BOT[0]-BG_TOP[0]) * int(feat["num"]) / 5),
                  int(BG_TOP[1] + (BG_BOT[1]-BG_TOP[1]) * int(feat["num"]) / 5),
                  int(BG_TOP[2] + (BG_BOT[2]-BG_TOP[2]) * int(feat["num"]) / 5)))

    inner_x = cx + 30
    inner_w = W - PADDING * 2 - 40
    text_w = inner_w - 10

    iy = cy + 30

    # Number badge (top-right)
    badge_r = 36
    badge_cx = cx + W - PADDING * 2 - badge_r - 20
    badge_cy = cy + badge_r + 20
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                  badge_cx + badge_r, badge_cy + badge_r],
                 fill=PURPLE)
    nb = feat["num"]
    bbox = draw.textbbox((0, 0), nb, font=f_num)
    nw = bbox[2] - bbox[0]
    nh = bbox[3] - bbox[1]
    draw.text((badge_cx - nw // 2, badge_cy - nh // 2 - 2), nb, font=f_num, fill=WHITE)

    # Title row
    icon_text = feat["icon"] + "  " + feat["title"]
    draw.text((inner_x, iy), icon_text, font=f_title_med, fill=DARK)
    bbox = draw.textbbox((0, 0), icon_text, font=f_title_med)
    iy += bbox[3] - bbox[1] + 18

    # Desc
    desc_lines = wrap_text(feat["desc"], f_body, text_w - 10, draw)
    for line in desc_lines:
        draw.text((inner_x + 5, iy), line, font=f_body, fill=GRAY_TEXT)
        bbox = draw.textbbox((0, 0), line, font=f_body)
        iy += bbox[3] - bbox[1] + 10
    iy += 10

    # Pain / Solution boxes
    col_w = (text_w - 20) // 2
    box_top = iy

    # Measure box height
    pain_lines_all = [wrap_text(p, f_body_sm, col_w - 55, draw) for p in feat["pains"]]
    sol_lines_all  = [wrap_text(s, f_body_sm, col_w - 55, draw) for s in feat["solutions"]]
    box_content_h = 40
    for pl, sl in zip(pain_lines_all, sol_lines_all):
        lh = max(text_height(pl, f_body_sm, 6), text_height(sl, f_body_sm, 6))
        box_content_h += lh + 14
    box_content_h += 20
    box_h_actual = box_content_h

    # Pain box
    px1, py1 = inner_x, box_top
    px2, py2 = inner_x + col_w, box_top + box_h_actual
    rounded_rect(draw, px1, py1, px2, py2, 10, YELLOW_BG)
    draw.rounded_rectangle([px1, py1, px2, py2], radius=10, outline=YELLOW_BORDER, width=2)
    draw.rounded_rectangle([px1, py1, px1 + 5, py2], radius=3, fill=YELLOW_BORDER)

    # Solution box
    sx1, sy1 = inner_x + col_w + 20, box_top
    sx2, sy2 = inner_x + col_w * 2 + 20, box_top + box_h_actual
    rounded_rect(draw, sx1, sy1, sx2, sy2, 10, GREEN_BG)
    draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=10, outline=GREEN_BORDER, width=2)
    draw.rounded_rectangle([sx1, sy1, sx1 + 5, sy2], radius=3, fill=GREEN_BORDER)

    # Pain header
    piy = py1 + 14
    draw.text((px1 + 18, piy), "传统痛点", font=f_label, fill=YELLOW_TEXT)
    piy += 36

    # Solution header
    siy = sy1 + 14
    draw.text((sx1 + 18, siy), "AIPP 解决方案", font=f_label, fill=GREEN_TEXT)
    siy += 36

    for pl, sl in zip(pain_lines_all, sol_lines_all):
        row_h = max(text_height(pl, f_body_sm, 6), text_height(sl, f_body_sm, 6))
        # pain item
        draw.ellipse([px1 + 16, piy + 4, px1 + 26, piy + 14], fill=RED_MARK)
        for line in pl:
            draw.text((px1 + 34, piy), line, font=f_body_sm, fill=YELLOW_TEXT)
            bbox = draw.textbbox((0, 0), line, font=f_body_sm)
            piy += bbox[3] - bbox[1] + 6
        piy += 8
        # solution item
        draw.ellipse([sx1 + 16, siy + 4, sx1 + 26, siy + 14], fill=GREEN_BORDER)
        for line in sl:
            draw.text((sx1 + 34, siy), line, font=f_body_sm, fill=GREEN_TEXT)
            bbox = draw.textbbox((0, 0), line, font=f_body_sm)
            siy += bbox[3] - bbox[1] + 6
        siy += 8

    iy = box_top + box_h_actual + 20

    # Value highlight box
    val_lines = wrap_text(feat["value"], f_body, text_w - 30, draw)
    val_content_h = text_height(val_lines, f_body, 10)
    vx1, vy1 = inner_x, iy
    vx2, vy2 = inner_x + text_w, iy + val_content_h + 40
    rounded_rect(draw, vx1, vy1, vx2, vy2, 10, BLUE_BG)
    draw.rounded_rectangle([vx1, vy1, vx2, vy2], radius=10, outline=BLUE_BORDER, width=2)
    draw.rounded_rectangle([vx1, vy1, vx1 + 5, vy2], radius=3, fill=BLUE_BORDER)

    label = "核心价值"
    draw.text((vx1 + 18, vy1 + 12), label, font=f_label, fill=BLUE_TEXT)
    bbox = draw.textbbox((0, 0), label, font=f_label)
    viy = vy1 + 12 + bbox[3] - bbox[1] + 8
    for line in val_lines:
        draw.text((vx1 + 18, viy), line, font=f_body, fill=BLUE_TEXT)
        bbox = draw.textbbox((0, 0), line, font=f_body)
        viy += bbox[3] - bbox[1] + 10

    cy += card_h

# ── FOOTER ─────────────────────────────────────────────────────────────────
cy += GAP * 2
fx1, fy1 = PADDING, cy
fx2, fy2 = W - PADDING, cy + FOOTER_H
rounded_rect(draw, fx1, fy1, fx2, fy2, 20, (255, 255, 255, 30))
draw.rounded_rectangle([fx1, fy1, fx2, fy2], radius=20, outline=(255, 255, 255, 80), width=2)

# Footer title
ft = "AIPP 平台核心优势"
bbox = draw.textbbox((0, 0), ft, font=f_title_sm)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, fy1 + 28), ft, font=f_title_sm, fill=WHITE)

# Three value cards
cards = [
    ("⚡", "效率提升", "推广工作效率提升 10 倍"),
    ("💰", "成本降低", "运营成本降低 70%"),
    ("🎨", "零门槛上手", "无需专业技能即可使用"),
]
card_w = (W - PADDING * 2 - 60) // 3
card_top = fy1 + 90
for i, (icon, title, desc) in enumerate(cards):
    vcx = PADDING + i * (card_w + 30)
    vcy = card_top
    rounded_rect(draw, vcx, vcy, vcx + card_w, vcy + 120, 12, (255, 255, 255))
    # icon
    bbox = draw.textbbox((0, 0), icon, font=f_title_med)
    iw = bbox[2] - bbox[0]
    draw.text((vcx + (card_w - iw) // 2, vcy + 12), icon, font=f_title_med, fill=PURPLE)
    # title
    bbox = draw.textbbox((0, 0), title, font=f_label)
    tw2 = bbox[2] - bbox[0]
    draw.text((vcx + (card_w - tw2) // 2, vcy + 58), title, font=f_label, fill=PURPLE)
    # desc
    bbox = draw.textbbox((0, 0), desc, font=f_body_sm)
    dw = bbox[2] - bbox[0]
    draw.text((vcx + (card_w - dw) // 2, vcy + 88), desc, font=f_body_sm, fill=GRAY_TEXT)

# Footer tagline
tl = "让 AI 成为您的推广助手，开启智能营销新时代"
bbox = draw.textbbox((0, 0), tl, font=f_sub)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, card_top + 140), tl, font=f_sub, fill=(220, 220, 255))

# ── save ───────────────────────────────────────────────────────────────────
out = "/Users/ai06/Desktop/智能推广平台AIPP/aipp-poster.jpg"
img.save(out, "JPEG", quality=95)
print(f"Saved: {out}  ({W}x{total_h})")
