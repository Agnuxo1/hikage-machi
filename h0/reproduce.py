#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Francisco Angulo de Lafuente
"""Run H0 in a fresh, explicit folder; no credentials or GPU required."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    target = args.work_dir.expanduser().resolve()
    if target.exists():
        parser.error('Work directory already exists. Inspect/reuse its evidence; choose a fresh folder for a new run.')
    ancestor = target.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    if shutil.disk_usage(ancestor).free < 14 * 1024**3:
        parser.error('At least 14 GiB free is required')
    target.mkdir(parents=True)
    shutil.copytree(source / 'source_snapshot', target / 'source_snapshot')
    scripts = ['acquire_h0.py','gtfs_inventory.py','citygml_inventory.py','verify_h0.py']
    for script in scripts:
        shutil.copyfile(source / script, target / script)
    env = {**os.environ, 'CUDA_VISIBLE_DEVICES':'-1','OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4',
           'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}
    for script in scripts:
        subprocess.run([sys.executable,'-u',str(target / script)],cwd=target,env=env,check=True)
    print('H0 inventory and checks completed:', target)

if __name__ == '__main__':
    main()
