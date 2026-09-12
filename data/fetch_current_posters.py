# -*- coding: utf-8 -*-
"""
Fetch CURRENT poster paths from TMDB API for movies in t_video_info,
update the DB, and download the images locally.
This replaces the 2019-era paths from Kaggle train.csv (those files are
gone from TMDB's CDN - verified 404 across the board on 2026-09-12).

Prereqs:
  1. TMDB API key (free): themoviedb.org -> settings -> API
     -> put key into data/tmdb_key.txt (or TMDB_API_KEY env)
  2. Proxy: --proxy http://127.0.0.1:7890 (Moon365 running)

Usage:
  python fetch_current_posters.py --proxy http://127.0.0.1:7890            # movies missing local poster
  python fetch_current_posters.py --proxy ... --all                        # all movies
  python fetch_current_posters.py --proxy ... --ids 155,27205              # specific movies
"""
import argparse, os, sys, time
import pymysql
import requests

KEY_FILE = r'D:\movie-system\data\tmdb_key.txt'
DEST_DIRS = [
    r'D:\movie-system\backend\src\main\resources\static\posters',
    r'D:\movie-system\backend\target\classes\static\posters',
]

def get_key():
    key = os.environ.get('TMDB_API_KEY', '').strip()
    if not key and os.path.exists(KEY_FILE):
        key = open(KEY_FILE, encoding='utf-8').read().strip()
    if not key:
        print('ERROR: no TMDB key. Set TMDB_API_KEY env or create ' + KEY_FILE)
        raise SystemExit(1)
    return key

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None)
    ap.add_argument('--all', action='store_true', help='refresh every movie, not just ones missing local poster')
    ap.add_argument('--ids', default='', help='comma separated tmdb ids')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    key = get_key()
    for d in DEST_DIRS:
        os.makedirs(d, exist_ok=True)

    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='vidio_mangage_db', charset='utf8mb4')
    cur = conn.cursor()
    if args.ids:
        ids = [i.strip() for i in args.ids.split(',') if i.strip().isdigit()]
    elif args.all:
        cur.execute("SELECT video_id FROM t_video_info ORDER BY heat_score DESC")
        ids = [str(r[0]) for r in cur.fetchall()]
    else:
        # movies without a local poster file yet, hottest first
        cur.execute("SELECT video_id FROM t_video_info ORDER BY heat_score DESC")
        ids = [str(r[0]) for r in cur.fetchall()
               if not os.path.exists(os.path.join(DEST_DIRS[0], str(r[0]) + '.jpg'))]
    if args.limit:
        ids = ids[:args.limit]
    print('movies to process:', len(ids))

    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system)'

    ok = miss = 0
    for i, vid in enumerate(ids, 1):
        img_data = None
        try:
            r = sess.get('https://api.themoviedb.org/3/movie/' + vid,
                         params={'api_key': key}, proxies=proxies, timeout=15)
            if r.status_code == 200:
                pp = (r.json().get('poster_path') or '').strip()
                if pp:
                    cur.execute("UPDATE t_video_info SET poster_path=%s WHERE video_id=%s", (pp, vid))
                    conn.commit()
                    if not os.path.exists(os.path.join(DEST_DIRS[0], vid + '.jpg')):
                        ir = sess.get('https://image.tmdb.org/t/p/w500' + pp,
                                      proxies=proxies, timeout=20)
                        if ir.status_code == 200 and ir.content[:4] != b'<!DO':
                            img_data = ir.content
                            for d in DEST_DIRS:
                                with open(os.path.join(d, vid + '.jpg'), 'wb') as f:
                                    f.write(img_data)
                    ok += 1
                else:
                    miss += 1
            elif r.status_code == 404:
                miss += 1
            elif r.status_code == 401:
                print('ERROR: invalid TMDB API key (401)')
                raise SystemExit(1)
            elif r.status_code == 429:
                time.sleep(3)
        except Exception as e:
            print('net err on', vid, ':', str(e)[:80])
        if i % 50 == 0 or i == len(ids):
            print('progress %d/%d ok=%d miss=%d' % (i, len(ids), ok, miss))
        time.sleep(0.3)
    print('DONE. ok=%d miss=%d' % (ok, miss))
    conn.close()

if __name__ == '__main__':
    main()
