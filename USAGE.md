# Using the trained OWC surrogate

Install from the repository root:

```bash
pip install -e .
```

Single-condition prediction:

```python
from owc_surrogate import predict_efficiency

eta = predict_efficiency(
    wave_period=2.0,
    wave_amplitude=0.04,
    draft=0.35,
    front_wall_thickness=0.05293,
    chamber_width=0.78,
    opening_ratio=0.012,
    quadratic_damping=1.75,
    artificial_damping=125.0,
)
print(eta)
```

The 1500-row `d-b-a-Topt-efficiency` table in `results/` was produced with the full research model; it is kept separate from the compact callable deployment model.
