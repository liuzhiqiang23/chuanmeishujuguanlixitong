# -*- coding: utf-8 -*-
"""
用豆瓣补齐缺失的影片海报（TMDB 走不通时的替代方案）。

数据源：m.douban.com 的 rexxar 搜索接口（和 movie.douban.com/j/subject_suggest
不同域名——后者高频请求会被限流成空数组）。rexxar 返回的 cover_url 带裁剪参数
（高只有 120px），所以从里面取出照片 id 再拼成标准大图地址。

安全策略：只有当豆瓣返回的标题和数据库片名归一化后相等、或相似度 >= 0.8
时才下载，避免配错图。写两份目录：源码目录 + 运行时 target/classes（后者
让正在跑的后端立即生效，不用重启）。

用法: python fill_posters_from_douban.py [--limit N] [--dry]
"""
import argparse
import difflib
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:8000'
DEST_DIRS = [
    r'D:\movie-system\backend\src\main\resources\static\posters',
    r'D:\movie-system\backend\target\classes\static\posters',
]
UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
      'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')
HDR = {'User-Agent': UA, 'Referer': 'https://m.douban.com/'}
DELAY = 4.0
RETRY_WAIT = 25


def has_poster(vid):
    for d in DEST_DIRS:
        p = os.path.join(d, '%s.jpg' % vid)
        if os.path.isfile(p) and os.path.getsize(p) > 3000:
            return True
    return False


def norm(s):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', (s or '').lower())


def similarity(a, b):
    if not a or not b:
        return 0.0
    if a == b or a in b or b in a:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def api_post(path, payload):
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=body,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=20).read().decode('utf-8'))


def http_get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=timeout)


def load_all_videos():
    out, page = {}, 1
    while True:
        r = api_post('/api/admin/video/page/list', {'pageIndex': page, 'pageSize': 500})
        resp = r.get('response') or {}
        lst = resp.get('list') or []
        if not lst:
            break
        for m in lst:
            out[m.get('videoId')] = m.get('videoName') or ''
        if len(out) >= (resp.get('total') or 0) or page > 40:
            break
        page += 1
    return out


def douban_search(name):
    """返回 target 字典列表（title / cover_url / year）"""
    url = ('https://m.douban.com/rexxar/api/v2/search?q='
           + urllib.parse.quote(name) + '&type=movie&count=5')
    r = http_get(url, timeout=20)
    d = json.loads(r.read().decode('utf-8', 'replace'))
    items = (d.get('subjects') or {}).get('items') or []
    return [it.get('target') or {} for it in items]


def pick_best(name, hits):
    target = norm(name)
    best = None
    for h in hits:
        title = h.get('title') or ''
        cover = h.get('cover_url') or ''
        if not cover:
            continue
        score = similarity(target, norm(title))
        if best is None or score > best[2]:
            best = (title, cover, score)
    return best if best and best[2] >= 0.8 else None


def big_url(cover_url):
    """cover_url 带 imageView2 裁剪参数（h/120），取出照片 id 拼标准大图"""
    m = re.search(r'/(p\d+)\.', cover_url)
    if m:
        return 'https://img1.doubanio.com/view/photo/l/public/%s.jpg' % m.group(1)
    return cover_url


def save(vid, content):
    for d in DEST_DIRS:
        if not os.path.isdir(d):
            continue
        with open(os.path.join(d, '%s.jpg' % vid), 'wb') as f:
            f.write(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--dry', action='store_true', help='只查不下载')
    args = ap.parse_args()

    missing = json.load(open(r'D:\movie-system\shots\missing_posters.json', encoding='utf-8'))
    missing = missing[args.start:]
    if args.limit:
        missing = missing[:args.limit]
    print('待补: %d 部' % len(missing))

    print('拉取片名...')
    names = load_all_videos()
    print('后端影片数:', len(names))

    ok, skip, fail = [], [], []
    for n, vid in enumerate(missing, 1):
        name = names.get(vid)
        if not name:
            skip.append((vid, '(后端查不到片名)'))
            continue
        if not args.dry and has_poster(vid):
            ok.append(vid)
            print('[%3d/%d] HAVE %-8s %s (已存在)' % (n, len(missing), vid, name))
            continue
        try:
            hits = douban_search(name)
            best = pick_best(name, hits)
            if not best:
                skip.append((vid, '%s -> 无高分匹配(hits=%d)' % (name, len(hits))))
                print('[%3d/%d] SKIP %-8s %s (hits=%d)' % (n, len(missing), vid, name, len(hits)))
                time.sleep(DELAY)
                continue
            dtitle, cover, score = best
            if args.dry:
                print('[%3d/%d] DRY  %-8s %-22s -> %-22s (%.2f)' % (n, len(missing), vid, name, dtitle, score))
                ok.append(vid)
                time.sleep(DELAY)
                continue
            data = None
            for attempt in range(4):
                try:
                    data = http_get(big_url(cover), timeout=30).read()
                    break
                except urllib.error.HTTPError as he:
                    # 豆瓣对图片是短时限流：403 等一会儿重试就好
                    if he.code in (403, 429) and attempt < 3:
                        print('     限流(%s)，等 %d 秒重试 %d/3' % (he.code, RETRY_WAIT, attempt + 1))
                        time.sleep(RETRY_WAIT)
                        continue
                    raise
            if data is None:
                raise RuntimeError('重试后仍拿不到图片')
            if data[:3] != b'\xff\xd8\xff' or len(data) < 3000:
                skip.append((vid, '下到的不是有效 jpeg (%dB)' % len(data)))
                print('[%3d/%d] BAD  %-8s %s (%dB)' % (n, len(missing), vid, name, len(data)))
                time.sleep(DELAY)
                continue
            save(vid, data)
            ok.append(vid)
            print('[%3d/%d] OK   %-8s %-22s <- %-22s (%.2f) %dKB'
                  % (n, len(missing), vid, name, dtitle, score, len(data) // 1024))
            time.sleep(DELAY)
        except Exception as e:
            fail.append((vid, name, str(e)[:60]))
            print('[%3d/%d] ERR  %-8s %-22s %s' % (n, len(missing), vid, name, str(e)[:60]))
            time.sleep(DELAY)

    print()
    print('=' * 56)
    print('成功 %d / 跳过 %d / 失败 %d' % (len(ok), len(skip), len(fail)))
    if skip:
        print('--- 跳过 ---')
        for v, why in skip[:20]:
            print('  ', v, why)
    if fail:
        print('--- 失败 ---')
        for v, nm, why in fail[:20]:
            print('  ', v, nm, why)


if __name__ == '__main__':
    main()
