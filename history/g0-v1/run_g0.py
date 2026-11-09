"""Bounded GPU engineering checks; synthetic controls, no contest result."""
import argparse
import hashlib
import json
import math
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from shade_geometry import coordinates, hard_shadow, smooth_shadow, expected_periodic_wait_minutes


def reference_triangles(points, suns, p):
    """Independent NumPy Moller-Trumbore ray/triangle intersection reference."""
    cx, cy, w, d, h, a = p
    rotation = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    xy = np.array([[-w/2,-d/2], [w/2,-d/2], [w/2,d/2], [-w/2,d/2]]) @ rotation.T + [cx,cy]
    corners = np.column_stack([xy, np.full(4,h)])
    origins = np.column_stack([points, np.zeros(len(points))])
    hit = np.zeros((len(points),len(suns)), dtype=bool)
    for ids in [(0,1,2),(0,2,3)]:
        va,vb,vc = corners[list(ids)]
        e1,e2 = vb-va,vc-va
        pv = np.cross(suns,e2)
        det = pv @ e1
        inv = np.divide(1.0, det, out=np.zeros_like(det), where=np.abs(det)>1e-12)
        tv = origins-va
        u = (tv @ pv.T) * inv
        qv = np.cross(tv,e1)
        v = (qv @ suns.T) * inv
        distance = (qv @ e2)[:,None]*inv
        hit |= ((np.abs(det)>1e-12)[None,:] & (u>=-1e-12) & (v>=-1e-12) & (u+v<=1+1e-12) & (distance>0))
    return hit


def run(device):
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested managed GPU is unavailable; no CPU fallback")
    rng = np.random.default_rng(20261109)
    def tensor(x): return torch.as_tensor(x,dtype=torch.float64,device=device)
    points = rng.uniform(-8,8,(8192,2))
    suns = rng.normal(size=(16,3)); suns[:,2]=rng.uniform(0.2,1,16); suns/=np.linalg.norm(suns,axis=1)[:,None]
    p0 = np.array([0.3,0.2,2.4,1.6,2.8,0.4])
    tp,ts = tensor(points),tensor(suns)
    mismatch=0; comparisons=0
    for _ in range(12):
        p=np.array([*rng.uniform(-2,2,2),rng.uniform(2,4),rng.uniform(1.5,3),rng.uniform(2.2,3.5),rng.uniform(-math.pi,math.pi)])
        expected=reference_triangles(points,suns,p)
        observed=hard_shadow(tp,ts,tensor(p)).cpu().numpy()
        mismatch+=int(np.count_nonzero(expected!=observed)); comparisons+=expected.size
    assert mismatch==0, (mismatch,comparisons)

    boundary_points=tensor([[0,0],[2,0],[1,0],[1+1e-6,0],[1-1e-6,0]])
    boundary=hard_shadow(boundary_points,tensor([[0,0,1]]),tensor([0,0,2,2,2.5,0])).cpu().numpy().ravel().tolist()
    assert boundary==[True,False,True,False,True], boundary

    params=tensor(p0).requires_grad_(True)
    weights=1+0.02*tp[:,0:1]+0.01*tp[:,1:2]
    objective=(smooth_shadow(tp,ts,params)*weights).mean()
    objective.backward(); auto=params.grad.detach().cpu().numpy()
    fd=[]; eps=1e-5
    for i in range(6):
        plus=p0.copy(); minus=p0.copy(); plus[i]+=eps; minus[i]-=eps
        hi=(smooth_shadow(tp,ts,tensor(plus))*weights).mean().item()
        lo=(smooth_shadow(tp,ts,tensor(minus))*weights).mean().item()
        fd.append((hi-lo)/(2*eps))
    fd=np.array(fd)
    assert np.allclose(auto,fd,rtol=1e-4,atol=1e-7), (auto,fd)

    u,v=coordinates(tp,ts,tensor(p0))
    margin=torch.minimum((u.abs()-p0[2]/2).abs(),(v.abs()-p0[3]/2).abs())
    away=margin>0.5
    smooth=smooth_shadow(tp,ts,tensor(p0),tau=0.02)
    exact=hard_shadow(tp,ts,tensor(p0)).to(torch.float64)
    away_error=(smooth[away]-exact[away]).abs().max().item()
    assert away_error < 1e-8
    rejected=0
    for bad_sun in [[[1,0,0]],[[0,0,-1]],[[float('nan'),0,1]]]:
        try: hard_shadow(tp,tensor(bad_sun),tensor(p0))
        except ValueError: rejected+=1
    try: smooth_shadow(tp,ts,tensor(p0),tau=0)
    except ValueError: rejected+=1
    assert rejected==4

    expected_wait=expected_periodic_wait_minutes([10,30])
    arrivals=np.arange(4000)*0.01+0.005
    departures=np.array([10.,40.])
    numerical_wait=float(np.mean(departures[np.searchsorted(departures,arrivals)]-arrivals))
    assert abs(expected_wait-12.5)<1e-12 and abs(expected_wait-numerical_wait)<1e-10
    assert expected_periodic_wait_minutes([20])==10
    perf=[]
    for n in [16384,65536,262144]:
        benchmark_points=tensor(rng.uniform(-8,8,(n,2)))
        for _ in range(2): smooth_shadow(benchmark_points,ts,tensor(p0)).mean().item()
        samples=[]
        for _ in range(5):
            if device=="cuda": torch.cuda.synchronize()
            start=time.perf_counter()
            smooth_shadow(benchmark_points,ts,tensor(p0)).mean().item()
            if device=="cuda": torch.cuda.synchronize()
            samples.append(time.perf_counter()-start)
        perf.append({"ground_points":n,"sun_directions":16,"ray_queries":n*16,"median_wall_seconds":float(np.median(samples)),"repetitions_seconds":samples})
    return {
        "status":"passed", "scope":"G0 synthetic engineering controls only",
        "author":"Francisco Angulo de Lafuente", "ai_assistance":"Codex",
        "seed":20261109, "dtype":"float64", "device":device,
        "python":platform.python_version(), "numpy":np.__version__, "torch":torch.__version__,
        "gpu":torch.cuda.get_device_name(0) if device=="cuda" else None,
        "hard_reference":{"scenes":12,"comparisons":comparisons,"mismatches":mismatch},
        "boundary_control":{"observed":boundary,"passed":True},
        "gradient_control":{"automatic":auto.tolist(),"central_finite_difference":fd.tolist(),"epsilon":eps,"max_absolute_error":float(np.max(np.abs(auto-fd))),"passed":True},
        "away_from_edge_control":{"margin_metres":0.5,"tau_metres":0.02,"max_absolute_error":away_error},
        "negative_controls_rejected":rejected,
        "wait_control":{"periodic_headways_minutes":[10,30],"expected_wait_minutes":expected_wait,"independent_numerical_wait_minutes":numerical_wait,"naive_mean_headway_halved_minutes":10},
        "performance":perf,
        "peak_cuda_allocated_bytes":torch.cuda.max_memory_allocated() if device=="cuda" else None,
        "radiance_H1_validated":False, "real_city_or_GTFS_data_used":False,
        "Neuro3D_contribution_demonstrated":False, "clinical_effectiveness_claimed":False,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument('--device',choices=['cpu','cuda'],default='cuda');parser.add_argument('--output',default='g0-result.json');args=parser.parse_args()
    source=Path(__file__).resolve().parent
    try: result=run(args.device)
    except Exception as exc:
        result={"status":"failed","error_type":type(exc).__name__,"error":str(exc),"device":args.device}
        raise
    finally:
        result['recorded_utc']=datetime.now(timezone.utc).isoformat()
        result['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob('*') if p.is_file() and p.suffix in ['.py','.json'] and p.name!=Path(args.output).name}
        Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','device','hard_reference','negative_controls_rejected','peak_cuda_allocated_bytes']}),flush=True)
