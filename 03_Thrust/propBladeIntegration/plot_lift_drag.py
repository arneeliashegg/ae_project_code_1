"""
Plot lift and drag per blade section for V = 20 m/s at 8000 and 10000 RPM.

Usage:
    python plot_lift_drag.py                       # CSVs in the current folder
    python plot_lift_drag.py --dir path/to/csvs
    python plot_lift_drag.py --per-span            # plot N/m instead of N per section
"""
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

RPMS = (8000, 10000)
VELOCITY = 20  # m/s


def load(path, value_col):
    """Read a CSV and keep only V = 20 m/s and the selected RPMs."""
    df = pd.read_csv(path)
    df = df[(df["vzero"] == VELOCITY) & (df["rpm"].isin(RPMS))]
    return df.dropna(subset=[value_col]).sort_values(["rpm", "section"])


def make_plot(df, value_col, ylabel, title, outfile):
    fig, ax = plt.subplots(figsize=(8, 5))
    for rpm, grp in df.groupby("rpm"):
        ax.plot(grp["r_mid_m"] * 1000, grp[value_col], marker="o", label=f"{rpm} RPM")
        # label each point with its section number
        for _, row in grp.iterrows():
            ax.annotate(int(row["section"]), (row["r_mid_m"] * 1000, row[value_col]),
                        textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=7)
    ax.set_xlabel("Blade section mid-radius r [mm]  (labels = section number)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=200)
    print(f"Saved {outfile}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".", help="folder containing lift_out.csv and drag_out.csv")
    parser.add_argument("--per-span", action="store_true", help="plot force per unit span (N/m)")
    parser.add_argument("--out", default=".", help="output folder for the PNGs")
    args = parser.parse_args()

    d, out = Path(args.dir), Path(args.out)

    if args.per_span:
        lift_col, drag_col, unit = "lift_per_span_N_m", "drag_per_span_N/m", "N/m"
    else:
        lift_col, drag_col, unit = "lift_N", "Drag_N", "N"

    lift = load(d / "lift_out.csv", lift_col)
    drag = load(d / "drag_out.csv", drag_col)

    subtitle = f"V = {VELOCITY} m/s"
    make_plot(lift, lift_col, f"Lift [{unit}]", f"Lift per blade section ({subtitle})",
              out / "lift_per_section.png")
    make_plot(drag, drag_col, f"Drag [{unit}]", f"Drag per blade section ({subtitle})",
              out / "drag_per_section.png")
    plt.show()


if __name__ == "__main__":
    main()
