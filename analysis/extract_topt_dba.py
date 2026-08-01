"""Generate >=1000 d-b-a scenarios and extract model-predicted Topt.

Requires the source training CSV locally. Geometry triples are sampled only from
observed d-b-a combinations using farthest-point space-filling selection.

Note: the authoritative 1500-row table committed in ``results/`` was generated
with the full 1600-tree research model (independent-test R2=0.9839). Re-running
this script uses the compact GitHub deployment surrogate, so small differences
from that table are expected.
"""
from pathlib import Path
import argparse, csv
import numpy as np
from owc_surrogate import find_optimal_period


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",type=Path,required=True)
    ap.add_argument("--out",type=Path,default=Path("results/dba_Topt_efficiency_1500.csv"))
    ap.add_argument("--n",type=int,default=1500)
    args=ap.parse_args()
    rows=[]
    with args.csv.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try: rows.append(tuple(float(r[k]) for k in ["draft","chamber_width","opening_ratio"]))
            except Exception: pass
    geom=np.unique(np.asarray(rows,float),axis=0)
    q05=np.quantile(geom,.05,axis=0); q95=np.quantile(geom,.95,axis=0); z=(geom-q05)/(q95-q05)
    start=int(np.argmin(((z-.5)**2).sum(1))); sel=[start]; mind=((z-z[start])**2).sum(1); mind[start]=-1
    for _ in range(1,args.n):
        j=int(np.argmax(mind)); sel.append(j); d2=((z-z[j])**2).sum(1); active=mind>=0
        mind[active]=np.minimum(mind[active],d2[active]); mind[j]=-1
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["d","b","a","Topt","efficiency"]); w.writeheader()
        for d,b,a in geom[sel]:
            opt=find_optimal_period(draft=d,chamber_width=b,opening_ratio=a)
            w.writerow({"d":d,"b":b,"a":a,"Topt":opt["Topt"],"efficiency":opt["efficiency"]})

if __name__=="__main__": main()
