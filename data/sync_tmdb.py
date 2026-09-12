# -*- coding: utf-8 -*-
"""
Sync "real-time" movies from TMDB API into t_video_info (+ posters).
Prereqs:
  1. TMDB API key (free): register at themoviedb.org -> settings -> API
  2. Network: api.themoviedb.org needs a proxy from CN networks.
Usage:
  set TMDB_API_KEY=xxx  (or put the key into data/tmdb_key.txt)
  python sync_tmdb.py --proxy http://127.0.0.1:7890 --pages 3
"""
import argparse, os, time
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
        sys_exit('TMDB API key not found. Set TMDB_API_KEY env or create ' + KEY_FILE)
    return key

def sys_exit(msg):
    print('ERROR:', msg)
    raise SystemExit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None)
    ap.add_argument('--pages', type=int, default=3, help='pages per list, 20 movies/page')
    ap.add_argument('--lang', default='zh-CN')
    args = ap.parse_args()

    api_key = get_key()
    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system sync)'

    movies = {}
    def fetch_page(lst, page):
        # 代理节点对 TMDB 时通时断，每页多重试扛过断连窗口
        for att, wait in enumerate((2, 5, 9, 14), 1):
            try:
                r = sess.get('https://api.themoviedb.org/3/movie/' + lst,
                             params={'api_key': api_key, 'language': args.lang, 'page': page},
                             proxies=proxies, timeout=25)
                if r.status_code == 200:
                    data = r.json().get('results', [])
                    for m in data:
                        movies[m['id']] = m
                    print(lst, 'page', page, 'ok (%d items), cum=%d' % (len(data), len(movies)))
                    return
                print(lst, 'page', page, 'HTTP', r.status_code)
                if r.status_code == 401:
                    return
            except Exception as e:
                print(lst, 'page', page, 'attempt', att, 'FAILED:', str(e)[:80])
            time.sleep(wait)
    for lst in ('now_playing', 'popular', 'top_rated'):
        for page in range(1, args.pages + 1):
            fetch_page(lst, page)
            time.sleep(0.4)
    if not movies:
        sys_exit('nothing fetched - check proxy/key')

    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='vidio_mangage_db', charset='utf8mb4')
    cur = conn.cursor()
    upserted = 0
    for mid, m in movies.items():
        poster = m.get('poster_path') or ''
        cur.execute(
            "SELECT video_id FROM t_video_info WHERE video_id=%s", (mid,))
        exists = cur.fetchone()
        if exists:
            cur.execute(
                "UPDATE t_video_info SET video_name=%s, original_title=%s, overview=%s,"
                "tagline=%s, popularity=%s, vote_average=%s, release_date=%s, poster_path=%s"
                " WHERE video_id=%s",
                (m.get('title'), m.get('original_title'), m.get('overview'), m.get('tagline') or '',
                 m.get('popularity') or 0, m.get('vote_average') or 0, m.get('release_date') or None,
                 poster, mid))
        else:
            cur.execute(
                "INSERT INTO t_video_info (video_name, original_title, overview, tagline, budget,"
                "revenue, popularity, heat_score, vote_average, vote_count, runtime, release_date,"
                "original_language, poster_path) VALUES (%s,%s,%s,%s,0,0,%s,%s,%s,%s,0,%s,%s,%s)",
                (m.get('title'), m.get('original_title'), m.get('overview'), m.get('tagline') or '',
                 m.get('popularity') or 0, m.get('popularity') or 0, m.get('vote_average') or 0,
                 m.get('vote_count') or 0, m.get('release_date') or None,
                 m.get('original_language') or '', poster))
        upserted += 1
        if poster:
            dest = os.path.join(DEST_DIRS[0], str(mid) + '.jpg')
            if not os.path.exists(dest):
                try:
                    r = sess.get('https://image.tmdb.org/t/p/w500' + poster,
                                 proxies=proxies, timeout=20)
                    if r.status_code == 200 and r.content[:4] != b'<!DO':
                        for d in DEST_DIRS:
                            with open(os.path.join(d, str(mid) + '.jpg'), 'wb') as f:
                                f.write(r.content)
                except Exception:
                    pass
                time.sleep(0.3)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM t_video_info")
    print('upserted:', upserted, '| t_video_info total now:', cur.fetchone()[0])
    conn.close()

if __name__ == '__main__':
    main()
