import sys, time, urllib.request, concurrent.futures as cf
base, ids, conc, rng = sys.argv[1], sys.argv[2].split(','), int(sys.argv[3]), sys.argv[4]
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def one(vid):
    t = time.time()
    try:
        req = urllib.request.Request(base + '/posters/' + vid + '.jpg')
        if rng != 'full':
            req.add_header('Range', 'bytes=0-' + rng)
        r = op.open(req, timeout=40); d = r.read()
        return (time.time() - t, len(d), None)
    except Exception as e:
        return (time.time() - t, 0, type(e).__name__)
t0 = time.time()
with cf.ThreadPoolExecutor(conc) as ex:
    res = list(ex.map(one, ids))
wall = time.time() - t0
ok = [r for r in res if r[2] is None]; bad = [r for r in res if r[2] is not None]
ts = sorted(r[0] for r in ok) if ok else []
print('  %d张 并发%d 取%s: 成功 %d/%d  墙钟 %.1fs' % (len(ids), conc, rng, len(ok), len(ids), wall))
if ts: print('    单张 中位 %.2fs 最大 %.2fs | 总 %.0f KB' % (ts[len(ts)//2], ts[-1], sum(r[1] for r in ok)/1024))
if bad: print('    失败 %d 个: %s' % (len(bad), ', '.join('%s(%.0fs)' % (b[2], b[0]) for b in bad[:5])))
