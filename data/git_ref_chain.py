# -*- coding: utf-8 -*-
"""Walk static/admin reference chain from index.html (BFS over quoted asset refs).
Outputs: data/_git_need_add.txt (referenced-but-untracked), data/_git_orphans.txt."""
import os, re, subprocess, glob

root = os.path.normpath(os.path.join('backend', 'src', 'main', 'resources', 'static', 'admin'))
ASSET = re.compile(r'["\']([^"\']+\.(?:js|css|jpg|jpeg|png|svg|webp|gif|ico|woff2?|ttf))["\']')

seen = set()  # normalized lowercase paths fully handled

def resolve(src_file, ref):
    ref = ref.split('?')[0].split('#')[0]
    if not ref or ref.startswith(('http:', 'https:', 'data:')):
        return None
    base = os.path.dirname(src_file) if ref.startswith('.') else root
    full = os.path.normpath(os.path.join(base, ref))
    return full if os.path.isfile(full) else None

def walk(f):
    fl = f.lower()
    if fl in seen:
        return
    seen.add(fl)
    try:
        text = open(f, 'rb').read().decode('utf-8', 'ignore')
    except OSError:
        return
    for r in ASSET.findall(text):
        full = resolve(f, r)
        if not full:
            continue
        if full.lower().endswith(('.js', '.css')):
            walk(full)
        else:
            seen.add(full.lower())

index = os.path.normpath(os.path.join(root, 'index.html'))
walk(index)
print('referenced total:', len(seen))

all_files = {os.path.normpath(p) for p in
             glob.glob(os.path.join(root, '**', '*'), recursive=True) if os.path.isfile(p)}
tracked = set(subprocess.run(['git', 'ls-files', root], capture_output=True, text=True)
              .stdout.lower().splitlines())

need_add = sorted(p for p in all_files if p.lower() in seen and p.lower() not in tracked)
orphans = sorted(p for p in all_files if p.lower() not in seen and p.lower() != index.lower())
print('build files total:', len(all_files))
print('to add (referenced, untracked):', len(need_add))
print('orphans (not adding):', len(orphans))
with open('data/_git_need_add.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(need_add))
with open('data/_git_orphans.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(orphans))
