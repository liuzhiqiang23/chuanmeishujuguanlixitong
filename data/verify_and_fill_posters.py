# -*- coding: utf-8 -*-
"""
Verify posters against TMDB titles, then fill only SAFE missing ones.
Phase 1: sweep existing {id}.jpg files - delete when TMDB title mismatches DB
         video_name (kills wrong-movie posters incl. adult content).
Phase 2: for rows without a local poster, fetch /3/movie/{id} and keep ONLY
         on title match (no title check = no download).
Prereq: TMDB key in data/tmdb_key.txt; Moon365 on; pass --proxy.
"""
import argparse, difflib, os, re, time
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
        print('ERROR: no TMDB key'); raise SystemExit(1)
    return key

def norm(s):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', (s or '').lower())

def title_match(db_name, db_original, t_title, t_original):
    n1, o1 = norm(db_name), norm(db_original)
    n2, o2 = norm(t_title), norm(t_original)
    for a, b in ((n1, n2), (n1, o2), (o1, n2), (o1, o2)):
        if a and b:
            if a == b or a in b or b in a:
                return True
            if difflib.SequenceMatcher(None, a, b).ratio() >= 0.55:
                return True
    return False

def save_jpg(vid, content):
    for d in DEST_DIRS:
        with open(os.path.join(d, vid + '.jpg'), 'wb') as f:
            f.write(content)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proxy', default=None)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--ids', default='')
    ap.add_argument('--sweep', action='store_true', help='phase1: delete mismatched existing posters (default off)')
    args = ap.parse_args()
    key = get_key()
    for d in DEST_DIRS:
        os.makedirs(d, exist_ok=True)
    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (movie-system)'

    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                           database='movie_analytics_db', charset='utf8mb4')
    cur = conn.cursor()

    def tmdb_get(vid):
        for att, wait in enumerate((1, 3, 6), 1):
            try:
                r = sess.get('https://api.themoviedb.org/3/movie/' + vid,
                             params={'api_key': key, 'language': 'zh-CN'},
                             proxies=proxies, timeout=20)
                if r.status_code == 200:
                    return r.json()
                if r.status_code == 404:
                    return None
                if r.status_code == 401:
                    print('invalid key'); raise SystemExit(1)
            except Exception as e:
                print('net', vid, 'att', att, str(e)[:60])
            time.sleep(wait)
        return None

    # ---------- PHASE 1: sweep existing files (only with --sweep; off by default per user) ----------
    if args.sweep and not args.ids:
        files = [os.path.basename(f)[:-4] for f
                 in __import__('glob').glob(os.path.join(DEST_DIRS[0], '*.jpg'))]
        print('PHASE1 sweep %d existing posters...' % len(files))
        removed = kept = 0
        for i, vid in enumerate(files, 1):
            cur.execute("SELECT video_name, IFNULL(original_title,'') FROM t_video_info WHERE video_id=%s", (vid,))
            row = cur.fetchone()
            if not row:
                continue
            m = tmdb_get(vid)
            if m is None or m.get('adult'):
                reason = '404' if m is None else 'adult'
            elif title_match(row[0], row[1], m.get('title') or '', m.get('original_title') or ''):
                kept += 1
                continue
            else:
                reason = 'title mismatch: TMDB="%s" vs DB="%s"' % ((m.get('title') or '')[:30], row[0][:30])
            for d in DEST_DIRS:
                p = os.path.join(d, vid + '.jpg')
                if os.path.exists(p):
                    os.remove(p)
            cur.execute("UPDATE t_video_info SET poster_path=NULL WHERE video_id=%s", (vid,))
            conn.commit()
            removed += 1
            print('REMOVED %s (%s)' % (vid, reason))
            if i % 50 == 0:
                print('phase1 progress %d/%d removed=%d kept=%d' % (i, len(files), removed, kept))
            time.sleep(0.25)
        print('PHASE1 done. removed=%d kept=%d' % (removed, kept))

    # ---------- PHASE 2: fill missing (title-verified only) ----------
    if args.ids:
        ids = [i.strip() for i in args.ids.split(',') if i.strip().isdigit()]
    else:
        cur.execute("SELECT video_id FROM t_video_info ORDER BY heat_score DESC")
        ids = [str(r[0]) for r in cur.fetchall()
               if not os.path.exists(os.path.join(DEST_DIRS[0], str(r[0]) + '.jpg'))]
    if args.limit:
        ids = ids[:args.limit]
    print('PHASE2 fill %d missing...' % len(ids))
    ok = skip = fail = 0
    for i, vid in enumerate(ids, 1):
        cur.execute("SELECT video_name, IFNULL(original_title,'') FROM t_video_info WHERE video_id=%s", (vid,))
        row = cur.fetchone()
        if not row:
            continue
        m = tmdb_get(vid)
        if not m or m.get('adult') or not title_match(row[0], row[1],
                m.get('title') or '', m.get('original_title') or ''):
            skip += 1
            if i % 50 == 0:
                print('phase2 progress %d/%d ok=%d skip=%d fail=%d' % (i, len(ids), ok, skip, fail))
            time.sleep(0.25)
            continue
        pp = (m.get('poster_path') or '').strip()
        if pp:
            try:
                ir = sess.get('https://image.tmdb.org/t/p/w500' + pp,
                              proxies=proxies, timeout=20)
                if ir.status_code == 200 and ir.content[:4] != b'<!DO':
                    save_jpg(vid, ir.content)
                    cur.execute("UPDATE t_video_info SET poster_path=%s WHERE video_id=%s", (pp, vid))
                    conn.commit()
                    ok += 1
                else:
                    fail += 1
            except Exception:
                fail += 1
        else:
            fail += 1
        if i % 50 == 0:
            print('phase2 progress %d/%d ok=%d skip=%d fail=%d' % (i, len(ids), ok, skip, fail))
        time.sleep(0.3)
    print('ALL DONE. phase2 ok=%d skip=%d fail=%d' % (ok, skip, fail))
    conn.close()

if __name__ == '__main__':
    main()
