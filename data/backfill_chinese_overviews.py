# -*- coding: utf-8 -*-
"""
Backfill official Chinese overviews (TMDB language=zh-CN) into `overview`
for movies whose stored overview is pure ASCII (legacy TMDB-5000 English
dataset). Also backfills video_name/original_title when the zh title is
available and the stored name is still ASCII. video_id IS the TMDB id.
Hottest first.

Usage:
  python backfill_chinese_overviews.py --proxy http://127.0.0.1:7890
  python backfill_chinese_overviews.py --proxy ... --limit 500
  python backfill_chinese_overviews.py --proxy ... --ids 76341,27205
"""
import argparse, re, sys, time
import pymysql
import requests

KEY_FILE = r'D:\movie-system\data\tmdb_key.txt'

def get_key():
    key = open(KEY_FILE, encoding='utf-8').read().strip() if __import__('os').path.exists(KEY_FILE) else ''
    if not key:
        raise SystemExit('ERROR: no TMDB key in ' + KEY_FILE)
    return key

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None)
    ap.add_argument('--limit', type=int, default=100000)
    ap.add_argument('--ids', default='')
    args = ap.parse_args()

    key = get_key()
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='movie_analytics_db', charset='utf8mb4')
    cur = conn.cursor()
    if args.ids:
        rows = [(int(i),) for i in args.ids.split(',') if i.strip().isdigit()]
    else:
        # 纯 ASCII 简介的行（老英文数据集），最热优先
        cur.execute("SELECT video_id FROM t_video_info "
                    "WHERE overview IS NOT NULL AND overview != '' "
                    "AND overview NOT REGEXP '[^ -~]' "
                    "ORDER BY heat_score DESC, video_id DESC LIMIT %s", (args.limit,))
        rows = cur.fetchall()
    print('movies to translate:', len(rows))

    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system)'

    ok = kept = miss = 0
    for i, (vid,) in enumerate(rows, 1):
        for att, wait in enumerate((2, 5, 9), 1):   # 代理对 TMDB 时通时断，重试扛过去
            try:
                r = sess.get('https://api.themoviedb.org/3/movie/%d' % vid,
                             params={'api_key': key, 'language': 'zh-CN'},
                             proxies=proxies, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    zh_ov = (data.get('overview') or '').strip()
                    zh_title = (data.get('title') or '').strip()
                    orig = (data.get('original_title') or '').strip()
                    fields = {}
                    if zh_ov and re.search(r'[^\x00-\x7f]', zh_ov):
                        fields['overview'] = zh_ov
                    if zh_title and re.search(r'[^\x00-\x7f]', zh_title):
                        # 顺手把仍是英文名的行补上中文名
                        cur.execute("SELECT video_name FROM t_video_info WHERE video_id=%s", (vid,))
                        row = cur.fetchone()
                        if row and row[0] and not re.search(r'[^\x00-\x7f]', row[0]):
                            fields['video_name'] = zh_title
                            if orig:
                                fields['original_title'] = orig
                    if fields:
                        sets = ', '.join('%s=%%s' % k for k in fields)
                        cur.execute("UPDATE t_video_info SET %s WHERE video_id=%%s" % sets,
                                    tuple(fields.values()) + (vid,))
                        conn.commit()
                        ok += 1
                    else:
                        kept += 1   # TMDB 无中文简介，保留英文
                    break
                elif r.status_code == 404:
                    miss += 1
                    break
                elif r.status_code == 401:
                    raise SystemExit('ERROR: invalid TMDB key')
                elif r.status_code == 429:
                    time.sleep(3)
                    continue
                else:
                    time.sleep(wait)
            except SystemExit:
                raise
            except Exception as e:
                if att == 3:
                    print('net err on', vid, ':', str(e)[:80])
                    miss += 1
                else:
                    time.sleep(wait)
        if i % 50 == 0 or i == len(rows):
            print('progress %d/%d ok=%d nozh=%d miss=%d' % (i, len(rows), ok, kept, miss))
        time.sleep(0.25)
    print('DONE. translated=%d no_official_zh=%d not_found_or_err=%d' % (ok, kept, miss))
    conn.close()

if __name__ == '__main__':
    main()
