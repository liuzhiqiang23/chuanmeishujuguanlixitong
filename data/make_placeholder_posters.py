# -*- coding: utf-8 -*-
"""
给仍缺海报的影片生成统一占位图（豆瓣限流抓不全时的兜底）。

只写"确实没有海报文件"的那些 id，已下到的真海报一律不动。
写两份目录：源码目录 + 运行时 target/classes（后者让后端立即生效）。
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

DEST_DIRS = [
    r'D:\movie-system\backend\src\main\resources\static\posters',
    r'D:\movie-system\backend\target\classes\static\posters',
]
W, H = 300, 450
BG = (43, 43, 49)
FRAME = (70, 70, 78)
ICON = (86, 86, 98)
TEXT = (112, 112, 122)


def build_placeholder():
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 25, H - 25], outline=FRAME, width=2)
    # 播放三角
    cx, cy = W // 2, H // 2 - 18
    d.polygon([(cx - 21, cy - 29), (cx - 21, cy + 29), (cx + 30, cy)], fill=ICON)
    try:
        f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    except Exception:
        f = ImageFont.load_default()
    d.text((W // 2, cy + 92), '\u6682\u65e0\u6d77\u62a5', font=f, fill=TEXT, anchor='mm')
    return img


def main():
    missing = json.load(open(r'D:\movie-system\shots\missing_posters.json', encoding='utf-8'))
    img = build_placeholder()
    made, kept = [], []
    for vid in missing:
        paths = [os.path.join(d, '%s.jpg' % vid) for d in DEST_DIRS]
        if any(os.path.isfile(p) and os.path.getsize(p) > 3000 for p in paths):
            kept.append(vid)
            continue
        for p, d in zip(paths, DEST_DIRS):
            if os.path.isdir(d):
                img.save(p, quality=88)
        made.append(vid)
    print('\u5360\u4f4d\u56fe\u751f\u6210: %d \u90e8' % len(made))
    print('\u4fdd\u7559\u771f\u6d77\u62a5: %d \u90e8' % len(kept))


if __name__ == '__main__':
    main()
