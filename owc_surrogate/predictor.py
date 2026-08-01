from __future__ import annotations
from functools import lru_cache
from importlib.resources import files
import base64
import gzip
import json
import numpy as np
from xgboost import XGBRegressor

FEATURE_ORDER = (
    "wave_period", "wave_amplitude", "draft", "front_wall_thickness",
    "chamber_width", "opening_ratio", "quadratic_damping", "artificial_damping"
)

@lru_cache(maxsize=1)
def get_model_metadata() -> dict:
    path = files("owc_surrogate").joinpath("models/metadata.json")
    return json.loads(path.read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def _model() -> XGBRegressor:
    model_dir = files("owc_surrogate").joinpath("models")
    names = sorted(p.name for p in model_dir.iterdir() if p.name.startswith("xgboost_efficiency.json.gz.b64.part"))
    if not names:
        raise FileNotFoundError("Packaged XGBoost model chunks are missing")
    encoded = "".join(model_dir.joinpath(name).read_text(encoding="ascii") for name in names)
    model_json = gzip.decompress(base64.b64decode(encoded))
    m = XGBRegressor()
    m.load_model(bytearray(model_json))
    return m

def _vector(values: dict, validate_domain: bool = True) -> np.ndarray:
    missing = [f for f in FEATURE_ORDER if f not in values]
    if missing:
        raise TypeError(f"Missing required inputs: {missing}")
    md = get_model_metadata()["feature_domain"]
    out=[]
    for f in FEATURE_ORDER:
        x=float(values[f]); lo=float(md[f]["min"]); hi=float(md[f]["max"])
        if validate_domain and not (lo <= x <= hi):
            raise ValueError(f"{f}={x} is outside the training domain [{lo}, {hi}]")
        out.append(x)
    return np.asarray(out,dtype=np.float32)

def predict_efficiency(*, wave_period: float, wave_amplitude: float, draft: float,
                       front_wall_thickness: float, chamber_width: float,
                       opening_ratio: float, quadratic_damping: float,
                       artificial_damping: float, validate_domain: bool = True) -> float:
    """Predict OWC efficiency for one 8-factor condition."""
    vals=locals().copy(); vals.pop("validate_domain")
    return float(_model().predict(_vector(vals,validate_domain).reshape(1,-1))[0])

def predict_efficiency_batch(records, validate_domain: bool = True) -> np.ndarray:
    """Predict OWC efficiency for an iterable of dict-like records."""
    X=np.vstack([_vector(dict(r),validate_domain) for r in records])
    return _model().predict(X).astype(float)

def find_optimal_period(*, draft: float, chamber_width: float, opening_ratio: float,
                        wave_amplitude: float | None = None,
                        front_wall_thickness: float | None = None,
                        quadratic_damping: float | None = None,
                        artificial_damping: float | None = None,
                        t_min: float | None = None, t_max: float | None = None,
                        step: float = 0.001, validate_domain: bool = True) -> dict:
    """Convenience scan using the compact deployment model.

    The authoritative 1500-row research Topt table in ``results/`` was generated
    with the full 1600-tree research model, so small differences are expected.
    """
    md=get_model_metadata()["feature_domain"]
    ref={
        "wave_amplitude": md["wave_amplitude"]["median"] if wave_amplitude is None else wave_amplitude,
        "front_wall_thickness": md["front_wall_thickness"]["median"] if front_wall_thickness is None else front_wall_thickness,
        "quadratic_damping": md["quadratic_damping"]["median"] if quadratic_damping is None else quadratic_damping,
        "artificial_damping": md["artificial_damping"]["median"] if artificial_damping is None else artificial_damping,
    }
    lo=md["wave_period"]["min"] if t_min is None else float(t_min)
    hi=md["wave_period"]["max"] if t_max is None else float(t_max)
    n=int(np.floor((hi-lo)/step+1e-12))+1; T=lo+np.arange(n,dtype=float)*step
    if T[-1] < hi-1e-12: T=np.r_[T,hi]
    T[0],T[-1]=lo,hi
    records=[{"wave_period":t,"wave_amplitude":ref["wave_amplitude"],"draft":draft,
              "front_wall_thickness":ref["front_wall_thickness"],"chamber_width":chamber_width,
              "opening_ratio":opening_ratio,"quadratic_damping":ref["quadratic_damping"],
              "artificial_damping":ref["artificial_damping"]} for t in T]
    pred=predict_efficiency_batch(records,validate_domain=validate_domain); mx=float(pred.max())
    ids=np.flatnonzero(np.isclose(pred,mx,rtol=0,atol=1e-8)); cuts=np.where(np.diff(ids)>1)[0]
    st=np.r_[0,cuts+1]; en=np.r_[cuts,len(ids)-1]; lens=ids[en]-ids[st]+1; j=int(np.argmax(lens))
    i0,i1=int(ids[st[j]]),int(ids[en[j]]); return {"Topt":float((T[i0]+T[i1])/2),"efficiency":mx,
        "T_plateau_min":float(T[i0]),"T_plateau_max":float(T[i1])}
