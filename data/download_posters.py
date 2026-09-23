# -*- coding: utf-8 -*-
"""
Download movie posters from TMDB image CDN into local static dir.
Usage:
  python download_posters.py                 # all movies that have poster_path
  python download_posters.py --limit 300     # only first N (order by heat)
  python download_posters.py --proxy http://127.0.0.1:7890
Resumable: existing files are skipped. Re-run anytime to fill gaps.
"""
import argparse, os, sys, time
import pymysql
import requests

SIZES = ['w500']
DEST_DIRS = [
    r'D:\movie-system\backend\src\main\resources\static\posters',
    r'D:\movie-system\backend\target\classes\static\posters',
]
PLACEHOLDER = 'placeholder.svg'

def dest_path(video_id):
    return os.path.join(DEST_DIRS[0], str(video_id) + '.jpg')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None, help='e.g. http://127.0.0.1:7890')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    for d in DEST_DIRS:
        os.makedirs(d, exist_ok=True)

    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='movie_analytics_db', charset='utf8mb4')
    cur = conn.cursor()
    sql = ("SELECT video_id, poster_path FROM t_video_info "
           "WHERE poster_path IS NOT NULL AND poster_path<>'' "
           "ORDER BY heat_score DESC")
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    if args.limit:
        rows = rows[:args.limit]

    todo = [(vid, pp) for vid, pp in rows if not os.path.exists(dest_path(vid))]
    print('total with path: %d, to download: %d' % (len(rows), len(todo)))

    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    ok = fail = 0
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system poster fetcher)'
    for i, (vid, pp) in enumerate(todo, 1):
        url = 'https://image.tmdb.org/t/p/%s%s' % (SIZES[0], pp)
        data = None
        for attempt in (1, 2):
            try:
                r = sess.get(url, proxies=proxies, timeout=20)
                if r.status_code == 200 and r.content[:4] != b'<!DO':
                    data = r.content
                    break
            except Exception:
                pass
            time.sleep(1.5 * attempt)
        if data:
            for d in DEST_DIRS:
                with open(os.path.join(d, str(vid) + '.jpg'), 'wb') as f:
                    f.write(data)
            ok += 1
        else:
            fail += 1
        if i % 25 == 0 or i == len(todo):
            print('progress %d/%d ok=%d fail=%d' % (i, len(todo), ok, fail))
        time.sleep(0.35)
    print('DONE. ok=%d fail=%d. Missing posters will show placeholder.' % (ok, fail))

if __name__ == '__main__':
    main()
