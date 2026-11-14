#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Independent source counts and relationships, with an explicit failing exit code."""
from pathlib import Path
from collections import Counter
from datetime import date
import csv
import io
import json
import re
import sys
import zipfile
import numpy as np

BASE = Path(__file__).resolve().parent

def main():
    acq = json.loads((BASE / 'ACQUISITION.json').read_text(encoding='utf-8'))
    city = json.loads((BASE / 'CITYGML_INVENTORY.json').read_text(encoding='utf-8'))
    gtfs = json.loads((BASE / 'GTFS_INVENTORY.json').read_text(encoding='utf-8'))
    results = []
    def check(name, condition, measured):
        results.append({'test': name, 'pass': bool(condition), 'measured': measured})
    # Different algorithm: binary opening-tag count, not the lxml tree parser.
    counts = {}
    part_counts = {}
    with zipfile.ZipFile(BASE / acq['citygml']['path']) as z:
        for info in z.infolist():
            if info.filename.startswith('udx/bldg/') and info.filename.endswith('.gml'):
                total, parts, carry = 0, 0, b''
                with z.open(info) as raw:
                    while True:
                        block = raw.read(1024 * 1024)
                        if not block:
                            total += len(re.findall(rb'<bldg:Building(?=[\s>])', carry))
                            parts += len(re.findall(rb'<bldg:BuildingPart(?=[\s>])', carry))
                            break
                        text = carry + block
                        # Keep the suffix after the last opening '<' so a split tag is not double-counted.
                        split = text.rfind(b'<')
                        if split < 0:
                            carry = text
                            continue
                        head, carry = text[:split], text[split:]
                        total += len(re.findall(rb'<bldg:Building(?=[\s>])', head))
                        parts += len(re.findall(rb'<bldg:BuildingPart(?=[\s>])', head))
                counts[info.filename], part_counts[info.filename] = total, parts
    parser_counts = {r['member']: r['buildings'] for r in city['files']}
    check('independent_binary_building_count', counts == parser_counts,
          {'binary': sum(counts.values()), 'lxml': city['building_count'], 'files': len(counts),
           'mismatched_files': [n for n in counts if counts[n] != parser_counts.get(n)]})
    check('independent_binary_part_count', sum(part_counts.values()) == city['building_part_elements'],
          {'binary': sum(part_counts.values()), 'lxml': city['building_part_elements']})
    with (BASE / 'BUILDINGS.csv').open(encoding='utf-8', newline='') as f:
        buildings = list(csv.DictReader(f))
    ids = [r['gml_id'] for r in buildings]
    check('building_ids_and_complete_geometry', len(ids) == city['building_count'] == len(set(ids))
          and not city['coordinate_errors'] and not city['missing_building_ids'] and not city['buildings_without_pos_coordinates'],
          {'csv_rows': len(ids), 'unique_ids': len(set(ids)), 'expected_buildings': city['building_count'],
           'coordinate_errors': len(city['coordinate_errors']), 'no_coordinates': len(city['buildings_without_pos_coordinates'])})
    # Verify every building extent lies in its file's declared envelope at 1e-7 coordinate tolerance.
    envelopes = {Path(r['member']).name.split('_')[0]: r['envelope'] for r in city['files']}
    outside = []
    for r in buildings:
        lo = np.array([float(r[x]) for x in ['lat_min', 'lon_min', 'height_min']])
        hi = np.array([float(r[x]) for x in ['lat_max', 'lon_max', 'height_max']])
        env = envelopes[r['mesh']]
        if env is None or not np.isfinite([lo, hi]).all() or (lo > hi).any() or (lo < np.array(env[0]) - 1e-7).any() or (hi > np.array(env[1]) + 1e-7).any():
            outside.append(r['gml_id'])
    check('geometry_within_declared_envelopes', not outside, {'outside_count': len(outside), 'examples': outside[:10],
          'tolerance': '1e-7 in native coordinate units; numerical check only'})
    check('observed_crs_and_axis_order', city['crs_observed'] == ['http://www.opengis.net/def/crs/EPSG/0/6697']
          and [a['direction'] for a in city['epsg_6697_local_database']['axes']] == ['north', 'east', 'up'], city['epsg_6697_local_database'])
    # Independent CSV reader and explicit table indexing instead of DictReader.
    tables = {}
    with zipfile.ZipFile(BASE / acq['gtfs']['path']) as z:
        for member in z.namelist():
            if member.endswith('.txt'):
                with z.open(member) as raw, io.TextIOWrapper(raw, encoding='utf-8-sig', newline='') as f:
                    data = list(csv.reader(f))
                    tables[Path(member).stem] = (data[0], data[1:])
    row_counts = {k: len(v[1]) for k, v in tables.items() if k in gtfs['rows']}
    check('independent_gtfs_row_counts', row_counts == gtfs['rows'], row_counts)
    headers, stop_rows = tables['stops']
    sid, slat, slon = [headers.index(n) for n in ['stop_id', 'stop_lat', 'stop_lon']]
    stop_positions = {r[sid]: (float(r[slat]), float(r[slon])) for r in stop_rows}
    check('gtfs_stop_coordinates_unique_plausible', len(stop_positions) == len(stop_rows)
          and all(34 < lat < 35 and 133 < lon < 135 for lat, lon in stop_positions.values()),
          {'unique': len(stop_positions), 'rows': len(stop_rows), 'region_test': '34<lat<35;133<lon<135'})
    header, agency = tables['agency']
    zones = sorted({r[header.index('agency_timezone')] for r in agency})
    check('agency_timezone_observed', zones == ['Asia/Tokyo'], zones)
    chosen = date(2026, 11, 16)
    active = set()
    header, records = tables['calendar']
    for r in records:
        start = date.fromisoformat(r[header.index('start_date')][:4] + '-' + r[header.index('start_date')][4:6] + '-' + r[header.index('start_date')][6:])
        finish = date.fromisoformat(r[header.index('end_date')][:4] + '-' + r[header.index('end_date')][4:6] + '-' + r[header.index('end_date')][6:])
        weekday = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][chosen.weekday()]
        if start <= chosen <= finish and int(r[header.index(weekday)]) == 1:
            active.add(r[header.index('service_id')])
    header, records = tables['calendar_dates']
    for r in records:
        if r[header.index('date')] == '20261116':
            service = r[header.index('service_id')]
            if int(r[header.index('exception_type')]) == 1:
                active.add(service)
            elif int(r[header.index('exception_type')]) == 2:
                active.discard(service)
    header, trips = tables['trips']
    trip_ids = {r[header.index('trip_id')] for r in trips if r[header.index('service_id')] in active}
    check('independent_calendar_scenario', sorted(active) == gtfs['service_scenario']['active_service_ids']
          and len(trip_ids) == gtfs['service_scenario']['trips'],
          {'date': str(chosen), 'active': sorted(active), 'trips': len(trip_ids)})
    check('gtfs_references_and_times', all(n == 0 for n in gtfs['reference_errors'].values())
          and not gtfs['times']['invalid_rows'] and not gtfs['times']['duplicate_trip_sequence_pairs'],
          {'references': gtfs['reference_errors'], 'times': gtfs['times']})
    result = {'passed': all(r['pass'] for r in results), 'checks': results,
              'scope': 'Numerical/data consistency only. Not ground truth, operation, shadows, H1/H3/H4 or official contest receipt.'}
    (BASE / 'H0_CHECKS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
