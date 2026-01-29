"""
data_generation.py

Cost Efficiency Project (Process-agnostic / universal manufacturing)

Generates synthetic but realistic manufacturing process data:
- cycle time, efficiency, downtime, scrap
- costs: material, labor, energy, overhead
- derived metrics: units_per_hour, good_units_per_hour, cost_per_unit, cost_per_good_unit

Output:
- saves CSV into: data/cost_efficiency_data.csv
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass
class Config:
    n_rows: int = 5000
    seed: int = 42
    out_path: str = os.path.join("data", "cost_efficiency_data.csv")


def _clip(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.clip(x, lo, hi)


def _random_choice(rng: np.random.Generator, values, p, size: int):
    return rng.choice(values, size=size, p=p)


def generate_cost_efficiency_data(cfg: Config) -> pd.DataFrame:
    """
    Generate synthetic manufacturing process data (universal / non-CNC specific).

    Key idea:
    - units_per_hour = (3600 / cycle_time_sec) * efficiency * cavity
    - good_units_per_hour = units_per_hour * (1 - scrap_rate)
    - cost_per_unit uses: material + allocated hourly costs / units_per_hour
    - cost_per_good_unit accounts for scrap

    Returns:
        DataFrame with raw columns + engineered metrics.
    """
    rng = np.random.default_rng(cfg.seed)
    n = cfg.n_rows

    # --- Categorical dimensions (useful later in SQL/BI) ---
    plants = ["PL01", "PL02", "PL03"]
    lines = ["LINE_A", "LINE_B", "LINE_C", "LINE_D"]
    shifts = ["A", "B", "C"]  # 3-shift model

    plant = _random_choice(rng, plants, p=[0.45, 0.35, 0.20], size=n)
    line = _random_choice(rng, lines, p=[0.30, 0.30, 0.25, 0.15], size=n)
    shift = _random_choice(rng, shifts, p=[0.34, 0.33, 0.33], size=n)

    # Product families influence cycle time, cavity, and material cost
    product_family = _random_choice(
        rng,
        ["STANDARD", "PREMIUM", "HEAVY"],
        p=[0.55, 0.30, 0.15],
        size=n,
    )

    # --- Time dimension ---
    # Create timestamps over last ~120 days with minute resolution
    end = pd.Timestamp.today().floor("min")
    start = end - pd.Timedelta(days=120)
    timestamps = pd.to_datetime(
        rng.integers(start.value // 10**9, end.value // 10**9, size=n),
        unit="s",
    ).floor("min")

    # --- Process variables ---
    # Cycle time depends on product family (seconds/unit)
    # Use lognormal to keep positive and skewed realistic
    base_cycle = np.where(
        product_family == "STANDARD",
        rng.lognormal(mean=np.log(35), sigma=0.25, size=n),
        np.where(
            product_family == "PREMIUM",
            rng.lognormal(mean=np.log(45), sigma=0.28, size=n),
            rng.lognormal(mean=np.log(60), sigma=0.30, size=n),
        ),
    )
    cycle_time_sec = _clip(base_cycle, 10, 180)

    # Cavity: 1–4 (e.g., multi-cavity tooling / multi-part per cycle)
    cavity = np.where(
        product_family == "HEAVY",
        _random_choice(rng, [1, 2], p=[0.70, 0.30], size=n),
        _random_choice(rng, [1, 2, 4], p=[0.55, 0.35, 0.10], size=n),
    ).astype(int)

    # Efficiency (OEE-like factor portion) 0.60–0.98
    # Add small line effect: LINE_D tends to be weaker
    eff_base = rng.normal(loc=0.86, scale=0.06, size=n)
    eff_line_penalty = np.where(line == "LINE_D", -0.04, 0.0)
    efficiency_pct = _clip(eff_base + eff_line_penalty, 0.60, 0.98)

    # Downtime rate fraction 0–0.25 (higher downtime reduces effective output)
    # (We'll apply downtime as an additional multiplicative reduction)
    downtime_base = rng.beta(a=2.0, b=10.0, size=n)  # skew to low downtime
    downtime_rate = _clip(downtime_base + np.where(line == "LINE_D", 0.03, 0.0), 0.00, 0.25)

    # Scrap rate fraction 0–0.15
    scrap_base = rng.beta(a=2.0, b=18.0, size=n)  # usually low
    scrap_rate = _clip(
        scrap_base
        + np.where(product_family == "PREMIUM", 0.01, 0.0)
        + np.where(line == "LINE_D", 0.01, 0.0),
        0.00,
        0.15,
    )

    # --- Output metrics ---
    # units per hour BEFORE downtime (but AFTER efficiency and cavity)
    units_per_hour = (3600.0 / cycle_time_sec) * efficiency_pct * cavity

    # Apply downtime as reduction in effective running time
    effective_units_per_hour = units_per_hour * (1.0 - downtime_rate)

    # Good units per hour after scrap
    good_units_per_hour = effective_units_per_hour * (1.0 - scrap_rate)

    # --- Cost drivers ---
    # Material cost per unit differs by product family
    material_cost_per_unit = np.where(
        product_family == "STANDARD",
        rng.normal(loc=2.2, scale=0.35, size=n),
        np.where(
            product_family == "PREMIUM",
            rng.normal(loc=3.4, scale=0.50, size=n),
            rng.normal(loc=5.2, scale=0.80, size=n),
        ),
    )
    material_cost_per_unit = _clip(material_cost_per_unit, 0.8, 12.0)

    # Hourly costs (labor, energy, overhead) vary by plant and shift
    # labor €/hour (or PLN/hour, doesn't matter—unitless for portfolio)
    plant_labor_base = np.select(
        [plant == "PL01", plant == "PL02", plant == "PL03"],
        [55.0, 50.0, 47.0],
        default=50.0,
    )
    shift_factor = np.select([shift == "A", shift == "B", shift == "C"], [1.00, 1.03, 1.06], default=1.0)
    labor_cost_per_hour = plant_labor_base * shift_factor + rng.normal(0, 2.0, size=n)
    labor_cost_per_hour = _clip(labor_cost_per_hour, 35.0, 80.0)

    # energy cost per hour
    energy_cost_per_hour = rng.normal(loc=18.0, scale=4.0, size=n)
    energy_cost_per_hour += np.where(product_family == "HEAVY", 4.0, 0.0)
    energy_cost_per_hour = _clip(energy_cost_per_hour, 6.0, 40.0)

    # overhead per hour
    overhead_cost_per_hour = rng.normal(loc=22.0, scale=5.0, size=n)
    overhead_cost_per_hour = _clip(overhead_cost_per_hour, 8.0, 60.0)

    # Total hourly cost
    total_cost_per_hour = labor_cost_per_hour + energy_cost_per_hour + overhead_cost_per_hour

    # --- Unit cost metrics ---
    # Cost per produced unit (includes material + allocated hourly costs)
    # Avoid division by zero: clip effective_units_per_hour to a small positive value
    effective_units_per_hour_safe = _clip(effective_units_per_hour, 0.1, 10_000.0)
    cost_per_unit = material_cost_per_unit + (total_cost_per_hour / effective_units_per_hour_safe)

    # Cost per GOOD unit (accounts for scrap)
    good_units_per_hour_safe = _clip(good_units_per_hour, 0.1, 10_000.0)
    cost_per_good_unit = material_cost_per_unit + (total_cost_per_hour / good_units_per_hour_safe)

    # Optional: “loss cost” from scrap per produced unit (simple proxy)
    scrap_cost_per_unit_proxy = material_cost_per_unit * scrap_rate

    # --- Assemble dataset ---
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "plant": plant,
            "line": line,
            "shift": shift,
            "product_family": product_family,
            "cycle_time_sec": np.round(cycle_time_sec, 2),
            "cavity": cavity,
            "efficiency_pct": np.round(efficiency_pct, 4),
            "downtime_rate": np.round(downtime_rate, 4),
            "scrap_rate": np.round(scrap_rate, 4),
            "units_per_hour": np.round(units_per_hour, 2),
            "effective_units_per_hour": np.round(effective_units_per_hour, 2),
            "good_units_per_hour": np.round(good_units_per_hour, 2),
            "material_cost_per_unit": np.round(material_cost_per_unit, 2),
            "labor_cost_per_hour": np.round(labor_cost_per_hour, 2),
            "energy_cost_per_hour": np.round(energy_cost_per_hour, 2),
            "overhead_cost_per_hour": np.round(overhead_cost_per_hour, 2),
            "total_cost_per_hour": np.round(total_cost_per_hour, 2),
            "cost_per_unit": np.round(cost_per_unit, 3),
            "cost_per_good_unit": np.round(cost_per_good_unit, 3),
            "scrap_cost_per_unit_proxy": np.round(scrap_cost_per_unit_proxy, 3),
        }
    )

    # Helpful sorting for time-series work later
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def save_csv(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def main() -> Tuple[pd.DataFrame, str]:
    cfg = Config()
    df = generate_cost_efficiency_data(cfg)
    save_csv(df, cfg.out_path)

    # --- display settings for clean console output ---
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.expand_frame_repr", False)

    print("✅ Generated dataset:")
    print(f"- rows: {len(df):,}")
    print(f"- columns: {df.shape[1]}")
    print(f"- saved to: {cfg.out_path}")

    preview_cols = [
        "timestamp",
        "plant",
        "line",
        "shift",
        "product_family",
        "cycle_time_sec",
        "efficiency_pct",
        "downtime_rate",
        "scrap_rate",
        "effective_units_per_hour",
        "good_units_per_hour",
        "total_cost_per_hour",
        "cost_per_unit",
        "cost_per_good_unit",
    ]

    print("\nPreview (key columns):")
    print(df[preview_cols].head(5).to_markdown(index=False))

    return df, cfg.out_path


if __name__ == "__main__":
    main()
