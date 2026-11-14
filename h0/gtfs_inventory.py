#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Deterministic inventory of the pinned public Kotoden snapshot; no wait estimate."""
from pathlib import Path
from datetime import date, datetime, timezone
from collections import Counter
import csv
import hashlib
import io
import json
import math
import sys
import zipfile

BASE = Path(__file__).resolve().parent
PIN = '6c2b1c419d05b9aa3a34439509a3f038a1c516603c405275f31603fdb54b2de6'
SERVICE_DATE = date(2026, 11, 16)  # fixed Monday, explicitly a timetable scenario

def seconds(value):
    fields = value.split(':')
    if len(fields) != 3 or any(not f.isdigit() for f in fields):
        raise ValueError(f'Invalid GTFS time {value!r}')
    h, m, s = map(int, fields)
    if not 0 <= m < 60 or not 0 <= s < 60:
        raise ValueError(f'Invalid GTFS minute/second {value!r}')
    return h * 3600 + m * 60 + s

def main():
    acq = json.loads((BASE / 'ACQUISITION.json').read_text(encoding='utf-8'))
    path = BASE / acq['gtfs']['path']
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    if digest != PIN:
        raise ValueError('GTFS pin mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('GTFS CRC failure')
        if sum(i.file_size for i in z.infolist()) > 64 * 1024**2:
            raise ValueError('GTFS decompressed size cap')
        tables = {}
        for name in ['stops', 'routes', 'trips', 'stop_times', 'calendar', 'calendar_dates', 'feed_info']:
            member = name + '.txt'
            if member in z.namelist():
                with z.open(member) as raw, io.TextIOWrapper(raw, encoding='utf-8-sig', newline='') as f:
                    tables[name] = list(csv.DictReader(f))
    for name in ['stops', 'routes', 'trips', 'stop_times']:
        if not tables.get(name):
            raise ValueError(f'Missing/empty {name}')
    out = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': digest,
           'source': 'Kotoden Bus GTFS snapshot acquired 2026-11-10', 'status': 'MEASURED_INVENTORY',
           'rows': {k: len(v) for k, v in tables.items()}, 'ids': {}, 'reference_errors': {},
           'claims': 'Timetable metadata and counts, not observed operations or physical validation.'}
    keys = {'stops': 'stop_id', 'routes': 'route_id', 'trips': 'trip_id'}
    ids = {}
    for name, key in keys.items():
        c = Counter(r[key] for r in tables[name])
        ids[name] = set(c)
        out['ids'][name] = {'unique': len(c), 'empty': c.get('', 0),
                            'duplicates': {k: n for k, n in c.items() if n > 1}}
    out['reference_errors']['trip_route'] = sum(r['route_id'] not in ids['routes'] for r in tables['trips'])
    out['reference_errors']['stop_time_trip'] = sum(r['trip_id'] not in ids['trips'] for r in tables['stop_times'])
    out['reference_errors']['stop_time_stop'] = sum(r['stop_id'] not in ids['stops'] for r in tables['stop_times'])
    all_service_ids = {r['service_id'] for name in ['calendar', 'calendar_dates'] for r in tables.get(name, [])}
    out['reference_errors']['trip_service'] = sum(r['service_id'] not in all_service_ids for r in tables['trips'])
    positions = []
    invalid = []
    for r in tables['stops']:
        try:
            lat, lon = float(r['stop_lat']), float(r['stop_lon'])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('coordinate')
            positions.append({'stop_id': r['stop_id'], 'stop_name': r.get('stop_name', ''), 'lat': lat, 'lon': lon})
        except (ValueError, KeyError):
            invalid.append(r.get('stop_id', ''))
    out['coordinates'] = {'valid': len(positions), 'invalid_stop_ids': invalid,
                          'bounds_lat_lon': [min(r['lat'] for r in positions), min(r['lon'] for r in positions),
                                             max(r['lat'] for r in positions), max(r['lon'] for r in positions)] if positions else None}
    arr, dep, bad = [], [], []
    pairs = Counter()
    for r in tables['stop_times']:
        pairs[(r['trip_id'], r['stop_sequence'])] += 1
        try:
            arr.append(seconds(r['arrival_time']))
            dep.append(seconds(r['departure_time']))
        except ValueError:
            bad.append({'trip_id': r['trip_id'], 'sequence': r['stop_sequence']})
    out['times'] = {'invalid_rows': bad, 'arrivals_ge24h': sum(x >= 86400 for x in arr),
                    'departures_ge24h': sum(x >= 86400 for x in dep),
                    'latest_arrival_seconds': max(arr) if arr else None,
                    'duplicate_trip_sequence_pairs': sum(n > 1 for n in pairs.values())}
    ds = SERVICE_DATE.strftime('%Y%m%d')
    weekday = SERVICE_DATE.strftime('%A').lower()
    active = {r['service_id'] for r in tables.get('calendar', [])
              if r['start_date'] <= ds <= r['end_date'] and r[weekday] == '1'}
    additions, removals = set(), set()
    for r in tables.get('calendar_dates', []):
        if r['date'] == ds:
            if r['exception_type'] == '1': additions.add(r['service_id'])
            elif r['exception_type'] == '2': removals.add(r['service_id'])
            else: raise ValueError('Invalid exception_type')
    if additions & removals:
        raise ValueError('Conflicting same-day service exceptions')
    active = (active | additions) - removals
    trips_today = {r['trip_id'] for r in tables['trips'] if r['service_id'] in active}
    served = {r['stop_id'] for r in tables['stop_times'] if r['trip_id'] in trips_today}
    out['service_scenario'] = {'date': SERVICE_DATE.isoformat(), 'agency_timezone_required': 'Asia/Tokyo',
                               'active_service_ids': sorted(active), 'trips': len(trips_today),
                               'stops': len(served), 'interpretation': 'Scheduled service; actual operation unverified.'}
    (BASE / 'GTFS_INVENTORY.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    with (BASE / 'GTFS_STOPS.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['stop_id', 'stop_name', 'lat', 'lon'])
        writer.writeheader()
        writer.writerows(positions)
    print(json.dumps({'rows': out['rows'], 'reference_errors': out['reference_errors'],
                      'coordinates': out['coordinates'], 'times': out['times'],
                      'service_scenario': out['service_scenario']}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
