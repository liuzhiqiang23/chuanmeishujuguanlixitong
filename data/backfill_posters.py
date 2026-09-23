# -*- coding: utf-8 -*-
# Backfill t_video_info.poster_path from local TMDB csv files (BOM-safe).
import csv, io, os, pymysql

sources = [
    r'D:\movie-system\data\recommendation\tmdb_5000_movies.csv',
    r'D:\movie-system\data\train.csv',
]
mapping = {}
for path in sources:
    with io.open(path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig strips BOM
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        idcol = 'id' if 'id' in cols else (cols[0] if cols else None)
        has_pp = 'poster_path' in cols
        print(os.path.basename(path), '| id col:', repr(idcol), '| poster_path:', has_pp)
        if not has_pp:
            continue
        for row in reader:
            mid = (row.get(idcol) or '').strip()
            pp = (row.get('poster_path') or '').strip()
            if mid.isdigit() and pp and mid not in mapping:
                mapping[mid] = pp
print('poster paths collected:', len(mapping))

conn = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                       database='movie_analytics_db', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT video_id FROM t_video_info")
ids = [r[0] for r in cur.fetchall()]
updates = [(mapping[str(vid)], vid) for vid in ids if str(vid) in mapping]
cur.executemany("UPDATE t_video_info SET poster_path=%s WHERE video_id=%s", updates)
conn.commit()
cur.execute("SELECT COUNT(*) FROM t_video_info WHERE poster_path IS NOT NULL AND poster_path<>''")
print('updated:', len(updates), '| rows with poster now:', cur.fetchone()[0], '/', len(ids))
conn.close()
