#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Scientific plots from measured extents; no basemap or simulated sunlight."""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
BG, FG, MUTED, TEAL, ORANGE = '#0b1324', '#edf3fa', '#a9bbcf', '#55dfc7', '#ffbd69'

def main():
    out = BASE / 'figures'
    out.mkdir(exist_ok=True)
    with (BASE / 'BUILDINGS.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    points = np.array([[(float(r['lon_min']) + float(r['lon_max'])) / 2,
                        (float(r['lat_min']) + float(r['lat_max'])) / 2, int(r['lod2_elements'])] for r in rows])
    with (BASE / 'GTFS_STOPS.csv').open(encoding='utf-8', newline='') as f:
        stops = np.array([[float(r['lon']), float(r['lat'])] for r in csv.DictReader(f)])
    city = json.loads((BASE / 'CITYGML_INVENTORY.json').read_text(encoding='utf-8'))
    high = points[points[:, 2] == 1]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': FG, 'axes.labelcolor': MUTED,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'font.size': 12,
                         'axes.edgecolor': '#34435a', 'axes.facecolor': BG, 'figure.facecolor': BG})
    images = []
    for include_stops in [False, True]:
        fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=120)
        fig.subplots_adjust(top=.74, bottom=.20, left=.07, right=.97, wspace=.2)
        fig.text(.07, .93, 'HIKAGE-MACHI  /  TAKAMATSU', fontsize=23, weight='bold')
        fig.text(.07, .87, '268,154 building objects  |  2,160 with LOD2 elements  |  658 bus-stop records', fontsize=15, color=TEAL)
        fig.text(.07, .825, 'H0 measured data inventory. Geometry centres are display proxies; this is not a shadow map.', fontsize=11, color=MUTED)
        for ax in axes:
            ax.scatter(points[:, 0], points[:, 1], s=.15, c='#7690ac', alpha=.55, rasterized=True, label='Building extent centres')
            ax.scatter(high[:, 0], high[:, 1], s=1, c=TEAL, alpha=.85, label='LOD2 element present')
            if include_stops:
                ax.scatter(stops[:, 0], stops[:, 1], s=10, c=ORANGE, edgecolors=BG, linewidths=.2, label='Kotoden GTFS stops', zorder=4)
            ax.set_xlabel('Longitude / degrees')
            ax.set_ylabel('Latitude / degrees')
            ax.grid(alpha=.12)
            ax.set_aspect(1 / np.cos(np.deg2rad(34.3)))
            ax.set_anchor('N')
            ax.ticklabel_format(axis='both', style='plain', useOffset=False)
        axes[0].set_title('City-wide building dataset', loc='left', color=FG, pad=15)
        axes[0].set_xlim(points[:, 0].min() - .007, points[:, 0].max() + .007)
        axes[0].set_ylim(points[:, 1].min() - .007, points[:, 1].max() + .007)
        axes[1].set_title('Detail around the LOD2 subset', loc='left', color=FG, pad=15)
        axes[1].set_xlim(high[:, 0].min() - .003, high[:, 0].max() + .003)
        axes[1].set_ylim(high[:, 1].min() - .003, high[:, 1].max() + .003)
        axes[1].legend(loc='lower right', fontsize=9, facecolor=BG, labelcolor=FG, edgecolor='#34435a')
        fig.text(.07, .09, 'Layer comparison: ' + ('CityGML + GTFS overlay' if include_stops else 'CityGML building layer'), color=ORANGE, fontsize=13)
        fig.text(.07, .055, 'Sources: Takamatsu City / MLIT PLATEAU (2022 CityGML v4); Kotoden Bus GTFS (10 Nov 2026 snapshot), CC BY 4.0.', color=MUTED, fontsize=9)
        fig.text(.07, .026, 'Derived by Francisco Angulo de Lafuente  |  ORCID 0009-0001-1634-7063  |  No accuracy, cooling or energy benefit measured.', color=MUTED, fontsize=9)
        file = out / ('takamatsu_h0.png' if include_stops else 'takamatsu_buildings.png')
        fig.savefig(file, facecolor=BG)
        plt.close(fig)
        with Image.open(file) as image:
            images.append(image.resize((1280, 640)).convert('RGB'))
    images[0].save(out / 'takamatsu_layers.gif', save_all=True, append_images=[images[1]], duration=[1500, 2600], loop=0, optimize=True)
    fontdir = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    font = ImageFont.truetype(str(fontdir / 'DejaVuSans-Bold.ttf'), 66)
    small = ImageFont.truetype(str(fontdir / 'DejaVuSans.ttf'), 27)
    credit = ImageFont.truetype(str(fontdir / 'DejaVuSans.ttf'), 21)
    frames = []
    for i in range(12):
        image = Image.new('RGB', (1600, 360), BG)
        d = ImageDraw.Draw(image)
        d.text((70, 55), 'HIKAGE-MACHI', fill=FG, font=font)
        d.text((74, 150), 'Open urban solar-exposure research', fill=TEAL, font=small)
        d.text((74, 204), 'Synthetic controls + real-city data intake  /  Application in development', fill=MUTED, font=small)
        d.text((74, 288), 'Francisco Angulo de Lafuente  |  ORCID 0009-0001-1634-7063', fill=MUTED, font=credit)
        d.line((74, 259, 1520, 259), fill='#2a3b51', width=3)
        x = 74 + int((1520 - 74) * i / 11)
        d.line((74, 259, x, 259), fill=TEAL, width=5)
        d.ellipse((x - 7, 252, x + 7, 266), fill=TEAL)
        frames.append(image)
    frames[0].save(out / 'hikage_title.gif', save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)
    print(json.dumps({'buildings_plotted': len(points), 'stops_plotted': len(stops), 'lod2': len(high),
                      'files': [p.name for p in out.iterdir()]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
