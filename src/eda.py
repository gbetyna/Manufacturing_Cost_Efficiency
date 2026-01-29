"""
eda.py

Cost Efficiency Project - Exploratory Data Analysis (EDA)

Reads:
- data/cost_efficiency_data.csv

Creates:
- reports/figures/*.png  (plots)
- reports/tables/*.csv   (summary tables, correlations, worst cases)

Run:
    python .\src\eda.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# BUSINESS INSIGHTS (EDA SUMMARY) - PORTFOLIO NOTES
# ============================================================
#
# 1) Product family is the strongest driver of cost_per_good_unit:
#    - HEAVY has the highest median cost and the largest variability.
#    - PREMIUM is mid.
#    - STANDARD is the lowest and most stable.
#    (See: box_cost_good_by_product_family.png)
#
# 2) Lines and plants show relatively similar medians, but cost variability differs:
#    - Some lines exhibit higher spread (risk/instability) even if their median is similar.
#    (See: box_cost_good_by_line.png, box_cost_good_by_plant.png)
#
# 3) Shifts are broadly comparable (no strong structural shift effect on cost):
#    - Similar median and spread across A/B/C.
#    (See: box_cost_good_by_shift.png)
#
# 4) Main cost drivers behave as expected:
#    - Higher cycle time, downtime, and scrap increase cost_per_good_unit.
#    - Higher throughput (good_units_per_hour) reduces cost_per_good_unit.
#    (See scatter plots + correlation heatmap)
#
# 5) Correlations confirm the logic of the process:
#    - cost_per_good_unit correlates positively with material_cost_per_unit, cycle_time_sec,
#      scrap_rate, downtime_rate; and negatively with good_units_per_hour.
#    (See: corr_heatmap.png + correlation_matrix.csv)
#
# Practical implication:
# Improving throughput and reducing scrap/downtime typically yields stronger unit-cost gains
# than focusing only on hourly cost reduction.
#
# ============================================================


DATA_PATH = Path("data") / "cost_efficiency_data.csv"
FIG_DIR = Path("reports") / "figures"
TAB_DIR = Path("reports") / "tables"


def ensure_dirs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}. Run data_generation.py first.")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def basic_info(df: pd.DataFrame) -> None:
    print("\n=== BASIC INFO ===")
    print("Shape:", df.shape)

    print("\nMissing values (top 10):")
    print(df.isna().sum().sort_values(ascending=False).head(10))

    print("\nNumeric describe:")
    print(df.select_dtypes(include=[np.number]).describe().T)


# -----------------------------
# Plot helpers (matplotlib only)
# -----------------------------
def save_hist(df: pd.DataFrame, col: str, title: str, filename: str, bins: int = 40) -> None:
    plt.figure()
    df[col].hist(bins=bins)
    plt.title(title)
    plt.xlabel(col)
    plt.ylabel("count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename, dpi=160)
    plt.close()


def save_box_by_category(
    df: pd.DataFrame,
    value_col: str,
    cat_col: str,
    title: str,
    filename: str,
    show_fliers: bool = False,
) -> None:
    plt.figure()
    categories = sorted(df[cat_col].dropna().unique().tolist())
    data = [df.loc[df[cat_col] == c, value_col].values for c in categories]

    plt.boxplot(data, labels=categories, showfliers=show_fliers)
    plt.title(title)
    plt.xlabel(cat_col)
    plt.ylabel(value_col)
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename, dpi=160)
    plt.close()


def save_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    filename: str,
    sample: int = 1500,
) -> None:
    plt.figure()
    d = df.sample(n=min(sample, len(df)), random_state=42)
    plt.scatter(d[x], d[y], s=10)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename, dpi=160)
    plt.close()


def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=[np.number]).copy()
    corr = num.corr(numeric_only=True)
    return corr


def save_corr_heatmap(corr: pd.DataFrame, filename: str = "corr_heatmap.png") -> None:
    plt.figure(figsize=(10, 8))
    plt.imshow(corr.values)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Correlation heatmap (numeric features)")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(FIG_DIR / filename, dpi=160)
    plt.close()


# -----------------------------
# Tables / outputs for BI & SQL
# -----------------------------
def top_worst_cases(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    cols = [
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
        "material_cost_per_unit",
        "total_cost_per_hour",
        "cost_per_unit",
        "cost_per_good_unit",
    ]
    worst = df.sort_values("cost_per_good_unit", ascending=False).head(k)[cols]
    return worst


def aggregation_tables(df: pd.DataFrame) -> None:
    """
    Average KPIs by category (good for SQL/BI layer).
    Saves four CSV files into reports/tables/.
    """
    group_cols = ["plant", "line", "shift", "product_family"]
    metrics = [
        "cost_per_unit",
        "cost_per_good_unit",
        "good_units_per_hour",
        "scrap_rate",
        "downtime_rate",
        "efficiency_pct",
    ]

    for g in group_cols:
        agg = (
            df.groupby(g, as_index=False)[metrics]
            .mean()
            .sort_values("cost_per_good_unit", ascending=False)
        )
        agg.to_csv(TAB_DIR / f"avg_metrics_by_{g.lower()}.csv", index=False)


def main() -> None:
    ensure_dirs()
    df = load_data(DATA_PATH)

    # Quick sanity check in console
    basic_info(df)

    # =========================================================
    # 1) DISTRIBUTIONS (Histograms)
    # Why: to understand skew, spread, and typical ranges.
    # =========================================================
    save_hist(df, "cost_per_unit", "Distribution: cost_per_unit", "hist_cost_per_unit.png")
    save_hist(df, "cost_per_good_unit", "Distribution: cost_per_good_unit", "hist_cost_per_good_unit.png")
    save_hist(df, "cycle_time_sec", "Distribution: cycle_time_sec", "hist_cycle_time_sec.png")
    save_hist(df, "efficiency_pct", "Distribution: efficiency_pct", "hist_efficiency_pct.png")

    # =========================================================
    # 2) CATEGORY COMPARISONS (Boxplots)
    # Why: compare medians + variability across operational dimensions.
    # =========================================================
    save_box_by_category(
        df,
        "cost_per_good_unit",
        "plant",
        "Cost per good unit by plant",
        "box_cost_good_by_plant.png",
        show_fliers=False,
    )
    save_box_by_category(
        df,
        "cost_per_good_unit",
        "line",
        "Cost per good unit by line",
        "box_cost_good_by_line.png",
        show_fliers=False,
    )
    save_box_by_category(
        df,
        "cost_per_good_unit",
        "shift",
        "Cost per good unit by shift",
        "box_cost_good_by_shift.png",
        show_fliers=False,
    )
    save_box_by_category(
        df,
        "cost_per_good_unit",
        "product_family",
        "Cost per good unit by product family",
        "box_cost_good_by_product_family.png",
        show_fliers=False,
    )

    # =========================================================
    # 3) DRIVERS vs COST (Scatter plots)
    # Why: check monotonic relationships and sensitivity.
    # =========================================================
    save_scatter(
        df,
        "cycle_time_sec",
        "cost_per_good_unit",
        "cycle_time_sec vs cost_per_good_unit",
        "scatter_cycle_vs_costgood.png",
    )
    save_scatter(
        df,
        "efficiency_pct",
        "cost_per_good_unit",
        "efficiency_pct vs cost_per_good_unit",
        "scatter_efficiency_vs_costgood.png",
    )
    save_scatter(
        df,
        "downtime_rate",
        "cost_per_good_unit",
        "downtime_rate vs cost_per_good_unit",
        "scatter_downtime_vs_costgood.png",
    )
    save_scatter(
        df,
        "scrap_rate",
        "cost_per_good_unit",
        "scrap_rate vs cost_per_good_unit",
        "scatter_scrap_vs_costgood.png",
    )

    # =========================================================
    # 4) CORRELATIONS
    # Why: quantify relationships between numeric variables.
    # =========================================================
    corr = correlation_table(df)
    corr.to_csv(TAB_DIR / "correlation_matrix.csv")
    save_corr_heatmap(corr, "corr_heatmap.png")

    # =========================================================
    # 5) OUTLIERS / WORST CASES
    # Why: identify high-cost situations for root-cause analysis.
    # =========================================================
    worst = top_worst_cases(df, k=10)
    worst.to_csv(TAB_DIR / "top10_worst_cost_per_good_unit.csv", index=False)

    print("\n=== TOP 10 WORST (cost_per_good_unit) ===")
    print(worst.to_string(index=False))

    # =========================================================
    # 6) AGGREGATION TABLES (for SQL/Power BI)
    # =========================================================
    aggregation_tables(df)

    print("\n✅ EDA finished.")
    print(f"- Figures saved to: {FIG_DIR}")
    print(f"- Tables saved to: {TAB_DIR}")


if __name__ == "__main__":
    main()
