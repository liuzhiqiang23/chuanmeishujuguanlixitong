# -*- coding: utf-8 -*-
"""
生成小程序 tabBar 图标（81×81 PNG，深空科幻风：细线条 + 选中态霓虹发光）。

输出：miniprogram/images/tabbar/
    home.png / home-on.png        首页（房子）
    member.png / member-on.png    会员（五角星）
    mine.png / mine-on.png        我的（人形）

用法：.venv\\Scripts\\python.exe tools/make_tabbar_icons.py
说明：4 倍超采样绘制后缩放，保证 81px 下线条平滑；-on 版本叠加高斯模糊做辉光。
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "miniprogram", "images", "tabbar")

SIZE = 81          # tabBar 图标标准尺寸
SS = 4             # 超采样倍数
STROKE = 5         # 线条粗细（最终像素）

INACTIVE = (168, 190, 220, 255)   # #A8BEDC 未选中：冷调亮灰蓝（比原来的 #6B7699 亮）
ACTIVE = (0, 229, 255, 255)       # #00E5FF 主题霓虹青


def _canvas():
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def draw_home(d, color):
    """房子：屋顶折线 + 主体矩形"""
    s = SS
    st = STROKE * s
    d.line([(13 * s, 39 * s), (40.5 * s, 13 * s), (68 * s, 39 * s)],
           fill=color, width=st, joint="curve")
    d.rounded_rectangle([22 * s, 39 * s, 59 * s, 68 * s], radius=4 * s,
                        outline=color, width=st)
    d.line([(40.5 * s, 52 * s), (40.5 * s, 68 * s)], fill=color, width=st)


def draw_member(d, color):
    """会员：五角星（VIP）——内圈半径要够大，否则描边把中心糊成齿轮"""
    s = SS
    cx, cy, R, r = 40.5, 42.5, 27, 14.8
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append(((cx + rad * math.cos(ang)) * s, (cy + rad * math.sin(ang)) * s))
    d.polygon(pts, outline=color, width=STROKE * s)


def draw_mine(d, color):
    """我的：头部圆环 + 肩部弧线（细线风格，肩部不做成实心块）"""
    s = SS
    st = STROKE * s
    d.ellipse([28.5 * s, 14.5 * s, 52.5 * s, 38.5 * s], outline=color, width=st)
    d.arc([18 * s, 43 * s, 63 * s, 77 * s], start=180, end=360,
          fill=color, width=st)


def build(kind, color, glow):
    img, d = _canvas()
    {"home": draw_home, "member": draw_member, "mine": draw_mine}[kind](d, color)
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    if not glow:
        return img
    # 选中态：模糊副本垫底做霓虹辉光
    halo = img.filter(ImageFilter.GaussianBlur(3.2))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(halo)
    out.alpha_composite(halo)
    out.alpha_composite(img)
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    made = []
    for kind in ("home", "member", "mine"):
        for suffix, color, glow in (("", INACTIVE, False), ("-on", ACTIVE, True)):
            img = build(kind, color, glow)
            path = os.path.join(OUT_DIR, "%s%s.png" % (kind, suffix))
            img.save(path)
            made.append((os.path.basename(path), os.path.getsize(path)))
    for name, size in made:
        print("  %-16s %5d bytes" % (name, size))
    print("共 %d 个图标 → %s" % (len(made), OUT_DIR))

    # 预览拼图（深空底色，4 倍放大看细节）——便于人工核对
    zoom, pad = 3, 18
    cell = SIZE * zoom
    sheet = Image.new("RGBA", (cell * 3 + pad * 4, cell + pad * 2), (11, 18, 48, 255))
    for i, kind in enumerate(("home", "member", "mine")):
        for j, suffix in enumerate(("", "-on")):
            ic = Image.open(os.path.join(OUT_DIR, "%s%s.png" % (kind, suffix)))
            ic = ic.resize((cell, cell), Image.NEAREST)
            sheet.alpha_composite(ic, (pad + i * (cell + pad), pad if j == 0 else pad))
    # 上排未选中、下排选中 → 改为两行拼图
    h = cell * 2 + pad * 3
    sheet = Image.new("RGBA", (cell * 3 + pad * 4, h), (11, 18, 48, 255))
    for i, kind in enumerate(("home", "member", "mine")):
        for j, suffix in enumerate(("", "-on")):
            ic = Image.open(os.path.join(OUT_DIR, "%s%s.png" % (kind, suffix)))
            ic = ic.resize((cell, cell), Image.LANCZOS)
            sheet.alpha_composite(ic, (pad + i * (cell + pad), pad + j * (cell + pad)))
    sheet_path = os.path.join(ROOT, "tools", "tabbar_icons_preview.png")
    sheet.save(sheet_path)
    print("预览拼图（上=未选中，下=选中）→ %s" % sheet_path)


if __name__ == "__main__":
    main()
