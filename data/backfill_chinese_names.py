# -*- coding: utf-8 -*-
"""
Backfill official Chinese titles (TMDB language=zh-CN) into video_name
for movies whose name is pure ASCII (MovieLens legacy rows).
video_id IS the TMDB id. Hottest first.

Usage:
  python backfill_chinese_names.py --proxy http://127.0.0.1:7890            # top 300 by heat
  python backfill_chinese_names.py --proxy ... --limit 1000
  python backfill_chinese_names.py --proxy ... --ids 293660,211672
"""
import argparse, os, re, time
import pymysql
import requests

KEY_FILE = r'D:\movie-system\data\tmdb_key.txt'

def get_key():
    key = os.environ.get('TMDB_API_KEY', '').strip()
    if not key and os.path.exists(KEY_FILE):
        key = open(KEY_FILE, encoding='utf-8').read().strip()
    if not key:
        raise SystemExit('ERROR: no TMDB key in ' + KEY_FILE)
    return key

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None)
    ap.add_argument('--limit', type=int, default=300)
    ap.add_argument('--ids', default='')
    args = ap.parse_args()

    key = get_key()
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='vidio_mangage_db', charset='utf8mb4')
    cur = conn.cursor()
    if args.ids:
        rows = [(int(i),) for i in args.ids.split(',') if i.strip().isdigit()]
    else:
        cur.execute("SELECT video_id FROM t_video_info "
                    "WHERE video_name NOT REGEXP '[^ -~]' "
                    "ORDER BY heat_score DESC, video_id DESC LIMIT %s", (args.limit,))
        rows = cur.fetchall()
    print('movies to rename:', len(rows))

    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system)'

    ok = same = miss = 0
    for i, (vid,) in enumerate(rows, 1):
        try:
            r = sess.get('https://api.themoviedb.org/3/movie/%d' % vid,
                         params={'api_key': key, 'language': 'zh-CN'},
                         proxies=proxies, timeout=15)
            if r.status_code == 200:
                data = r.json()
                zh = (data.get('title') or '').strip()
                orig = (data.get('original_title') or '').strip()
                if not zh:
                    miss += 1
                elif re.search(r'[^\x00-\x7f]', zh):
                    cur.execute("UPDATE t_video_info SET video_name=%s, original_title=%s "
                                "WHERE video_id=%s", (zh, orig or zh, vid))
                    conn.commit()
                    ok += 1
                else:
                    # zh-CN title itself is ASCII (e.g. English-language film with
                    # no official Chinese name) - keep, but store original properly
                    same += 1
            elif r.status_code == 404:
                miss += 1
            elif r.status_code == 401:
                raise SystemExit('ERROR: invalid TMDB key')
            elif r.status_code == 429:
                time.sleep(3)
                continue
        except SystemExit:
            raise
        except Exception as e:
            print('net err on', vid, ':', str(e)[:80])
        if i % 50 == 0 or i == len(rows):
            print('progress %d/%d ok=%d nozh=%d miss=%d' % (i, len(rows), ok, same, miss))
        time.sleep(0.3)
    print('DONE. renamed=%d no_official_zh=%d not_found=%d' % (ok, same, miss))
    conn.close()

if __name__ == '__main__':
    main()
