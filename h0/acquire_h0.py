#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Acquire the single catalogued CityGML archive; reuse the exact cached GTFS."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
CACHE = BASE / 'source_snapshot'
LIMIT = 2 * 1024**3
GTFS_SHA = '6c2b1c419d05b9aa3a34439509a3f038a1c516603c405275f31603fdb54b2de6'

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(name, data):
    (BASE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    data = BASE / 'data'
    data.mkdir(exist_ok=True)
    receipt = BASE / 'ACQUISITION.json'
    if receipt.exists():
        raise RuntimeError('Existing acquisition: inspect and reuse it, do not repeat blindly.')
    catalogue = json.loads((CACHE / 'plateau_package.json').read_text(encoding='utf-8-sig'))['result']
    candidates = [r for r in catalogue['resources'] if r['name'] == 'CityGML（v4）']
    if len(candidates) != 1:
        raise ValueError('Expected exactly one CityGML v4 resource')
    url = candidates[0]['url']
    if not url.startswith('https://assets.cms.plateau.reearth.io/assets/'):
        raise ValueError('Unapproved archive host')
    gtfs = CACHE / 'bus_gtfs.zip'
    if sha(gtfs) != GTFS_SHA:
        raise ValueError('Cached GTFS changed')
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'status': 'RUNNING',
              'source_catalogue_sha256': sha(CACHE / 'plateau_package.json'),
              'citygml_url': url, 'source_catalogue_resource_id': candidates[0]['id'],
              'gtfs': {'path': 'source_snapshot/bus_gtfs.zip', 'sha256': GTFS_SHA, 'bytes': gtfs.stat().st_size,
                       'reused': True}, 'gpu': False}
    save('ACQUISITION.json', record)
    target = data / 'takamatsu_2022_citygml_v4.zip'
    partial = target.with_suffix('.zip.part')
    if target.exists() or partial.exists():
        raise RuntimeError('Archive/partial already exists; inspect before any retry')
    if shutil.disk_usage(data).free < 14 * 1024**3:
        raise RuntimeError('Less than 14 GiB free')
    started = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HikageMachi-Research/0.1 (+https://github.com/Agnuxo1/hikage-machi)'})
        with urllib.request.urlopen(req, timeout=60) as r, partial.open('xb') as out:
            size_header = r.headers.get('Content-Length')
            expected = int(size_header) if size_header else None
            if expected is not None and expected > LIMIT:
                raise ValueError('Archive exceeds compressed byte cap')
            record.update(final_url=r.geturl(), http_status=r.status, content_length=expected,
                          etag=r.headers.get('ETag'), last_modified=r.headers.get('Last-Modified'))
            h = hashlib.sha256()
            total = 0
            next_update = 0
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > LIMIT or time.monotonic() - started > 1200:
                    raise ValueError('Download byte or wall-time cap exceeded')
                h.update(chunk)
                out.write(chunk)
                if time.monotonic() >= next_update:
                    save('DOWNLOAD_PROGRESS.json', {'bytes': total, 'expected': expected,
                         'elapsed_seconds': round(time.monotonic() - started, 2)})
                    print(f'CityGML {total} / {expected} bytes', flush=True)
                    next_update = time.monotonic() + 25
            if expected is not None and total != expected:
                raise ValueError('Incomplete response')
        if h.hexdigest() != 'd44976d25c155f78f5090dc8cd1014f816ca03c46e761c9fa8c37d8c39363641':
            raise ValueError('CityGML source changed from the recorded H0 snapshot')
        partial.replace(target)
        record.update(status='DOWNLOADED', completed_utc=datetime.now(timezone.utc).isoformat(),
                      citygml={'path': 'data/takamatsu_2022_citygml_v4.zip', 'bytes': total, 'sha256': h.hexdigest()},
                      elapsed_seconds=time.monotonic() - started)
        save('ACQUISITION.json', record)
        print(json.dumps({'status': record['status'], 'bytes': total, 'sha256': h.hexdigest()}), flush=True)
    except Exception as exc:
        record.update(status='FAILED', error_type=type(exc).__name__, error=str(exc),
                      elapsed_seconds=time.monotonic() - started)
        save('ACQUISITION.json', record)
        raise

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
