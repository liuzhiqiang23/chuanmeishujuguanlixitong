import sys, time, urllib.request, concurrent.futures as cf
base = sys.argv[1]; ids = sys.argv[2].split(','); conc = int(sys.argv[3])
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def one(vid):
    t = time.time()
    try:
        r = op.open(base + '/posters/' + vid + '.jpg', timeout=45)
        d = r.read()
        return (time.time() - t, len(d), None)
    except Exception as e:
        return (time.time() - t, 0, type(e).__name__)
t0 = time.time()
with cf.ThreadPoolExecutor(conc) as ex:
    res = list(ex.map(one, ids))
wall = time.time() - t0
ok = [r for r in res if r[2] is None]
bad = [r for r in res if r[2] is not None]
print('  base=%s' % base)
print('  成功 %d/%d  墙钟总耗时 %.2fs' % (len(ok), len(ids), wall))
if ok:
    ts = sorted(r[0] for r in ok); sizes = sum(r[1] for r in ok)
    print('  单张: min %.2fs / 中位 %.2fs / max %.2fs' % (ts[0], ts[len(ts)//2], ts[-1]))
    print('  总字节 %d (%.0f KB)  平均吞吐 %.0f KB/s' % (sizes, sizes/1024, sizes/1024/wall))
if bad:
    print('  失败: %s' % ', '.join('%s(%.2fs)' % (b[2], b[0]) for b in bad))
