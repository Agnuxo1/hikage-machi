#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Stream actual building geometry without textures, external schemas or extraction."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import json
import sys
import time
import zipfile
import numpy as np
from lxml import etree
from pyproj import CRS

BASE = Path(__file__).resolve().parent
BLDG = 'http://www.opengis.net/citygml/building/2.0'
GML = 'http://www.opengis.net/gml'
NS = {'b': BLDG, 'g': GML}
BUILDING = '{' + BLDG + '}Building'
ENVELOPE = '{' + GML + '}Envelope'
CAP = 12 * 1024**3

def main():
    started = time.monotonic()
    acq = json.loads((BASE / 'ACQUISITION.json').read_text(encoding='utf-8'))
    if acq['status'] != 'DOWNLOADED':
        raise RuntimeError('Acquisition incomplete')
    path = BASE / acq['citygml']['path']
    with path.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != acq['citygml']['sha256']:
            raise ValueError('CityGML archive changed')
    known_ids = set()
    duplicate_ids = []
    missing_ids = 0
    parts_count = 0
    coord_errors = []
    empty_geometry = []
    file_stats = []
    lod = Counter()
    rows = []
    with zipfile.ZipFile(path) as z, (BASE / 'BUILDINGS.csv').open('w', encoding='utf-8', newline='') as out:
        files = sorted([i for i in z.infolist() if i.filename.startswith('udx/bldg/') and i.filename.endswith('.gml')], key=lambda i: i.filename)
        total_bytes = sum(i.file_size for i in files)
        if not files or total_bytes > CAP:
            raise ValueError('Building GML absent or exceeds selected-read byte cap')
        writer = csv.DictWriter(out, fieldnames=['gml_id', 'mesh', 'lod1_elements', 'lod2_elements',
                                   'lat_min', 'lon_min', 'height_min', 'lat_max', 'lon_max', 'height_max'])
        writer.writeheader()
        for index, info in enumerate(files):
            fs = {'member': info.filename, 'bytes': info.file_size, 'buildings': 0,
                  'parts': 0, 'crs': [], 'envelope': None, 'lod1_elements': 0, 'lod2_elements': 0}
            with z.open(info) as raw:
                # no DTD load, entity expansion, schema download, XInclude or XLink dereferencing
                for _, element in etree.iterparse(raw, events=('end',), tag=(BUILDING, ENVELOPE),
                         resolve_entities=False, load_dtd=False, no_network=True, huge_tree=True):
                    if element.tag == ENVELOPE:
                        srs = element.get('srsName')
                        if srs and srs not in fs['crs']:
                            fs['crs'].append(srs)
                        if fs['envelope'] is None:
                            low = element.find('g:lowerCorner', NS)
                            high = element.find('g:upperCorner', NS)
                            if low is not None and high is not None:
                                fs['envelope'] = [list(map(float, low.text.split())), list(map(float, high.text.split()))]
                        continue
                    fs['buildings'] += 1
                    gid = element.get('{' + GML + '}id', '')
                    if not gid:
                        missing_ids += 1
                    if gid in known_ids:
                        duplicate_ids.append(gid)
                    known_ids.add(gid)
                    part_n = len(element.findall('.//b:BuildingPart', NS))
                    fs['parts'] += part_n
                    parts_count += part_n
                    has1 = any(e.tag.startswith('{' + BLDG + '}lod1') for e in element.iter())
                    has2 = any(e.tag.startswith('{' + BLDG + '}lod2') for e in element.iter())
                    lod['with_lod1_elements'] += has1
                    lod['with_lod2_elements'] += has2
                    fs['lod1_elements'] += has1
                    fs['lod2_elements'] += has2
                    low = np.full(3, np.inf)
                    high = np.full(3, -np.inf)
                    present = False
                    for tag in ['posList', 'pos']:
                        for position in element.iter('{' + GML + '}' + tag):
                            arr = np.fromstring(position.text or '', sep=' ', dtype=np.float64)
                            dim = int(position.get('srsDimension', '3'))
                            if dim != 3 or not arr.size or arr.size % 3 or not np.isfinite(arr).all():
                                coord_errors.append({'id': gid, 'tag': tag, 'dimension': dim, 'values': arr.size})
                                continue
                            coords = arr.reshape(-1, 3)
                            low = np.minimum(low, coords.min(axis=0))
                            high = np.maximum(high, coords.max(axis=0))
                            present = True
                    if present:
                        writer.writerow(dict(zip(writer.fieldnames, [gid, Path(info.filename).name.split('_')[0],
                            int(has1), int(has2), *low.tolist(), *high.tolist()])))
                    else:
                        empty_geometry.append(gid)
                    # Free this cityObjectMember and preceding siblings after all its geometry is read.
                    parent = element.getparent()
                    element.clear()
                    if parent is not None:
                        parent.clear()
                        while parent.getprevious() is not None:
                            del parent.getparent()[0]
            file_stats.append(fs)
            if index % 20 == 0 or index == len(files) - 1:
                progress = {'files_done': index + 1, 'files_total': len(files), 'buildings': sum(s['buildings'] for s in file_stats),
                            'elapsed_seconds': round(time.monotonic() - started, 2)}
                (BASE / 'CITYGML_PROGRESS.json').write_text(json.dumps(progress), encoding='utf-8')
                print(json.dumps(progress), flush=True)
    crs = CRS.from_epsg(6697)
    result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'archive_sha256': acq['citygml']['sha256'],
              'status': 'MEASURED_BUILDING_INVENTORY', 'building_gml_files': len(file_stats),
              'selected_uncompressed_bytes_read': total_bytes, 'building_count': sum(s['buildings'] for s in file_stats),
              'building_unique_ids': len(known_ids), 'duplicate_building_ids': duplicate_ids, 'missing_building_ids': missing_ids,
              'building_part_elements': parts_count, 'lod_element_presence': dict(lod),
              'coordinate_errors': coord_errors, 'buildings_without_pos_coordinates': empty_geometry,
              'crs_observed': sorted({s for fs in file_stats for s in fs['crs']}),
              'epsg_6697_local_database': {'name': crs.name, 'axes': [{'name': a.name, 'direction': a.direction, 'unit': a.unit_name} for a in crs.axis_info]},
              'crc_scope': f'All {len(file_stats)} selected building GML members fully streamed; ZipExtFile checks CRC at EOF. Other members not CRC-tested.',
              'files': file_stats, 'elapsed_seconds': time.monotonic() - started,
              'limitations': ['LOD element presence does not validate surface topology.', 'Bounding boxes are geometric extents, not shadows or municipal boundaries.',
                              'Source vintage differs from current timetable; current-day building accuracy unverified.', 'No textures, terrain or other feature classes used.']}
    (BASE / 'CITYGML_INVENTORY.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['files', 'coordinate_errors', 'buildings_without_pos_coordinates', 'duplicate_building_ids']}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
