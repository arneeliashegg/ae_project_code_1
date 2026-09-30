"""Drag per blade section and total blade drag via numerical integration.

Uses velocities.py (unchanged) for V_local, AoA and Cd.
D_i  = 0.5 * rho * V_local^2 * S_i * Cd_i,   S_i = chord_i * delta_r_i
D'_i = D_i / delta_r_i  (drag per unit span, N/m)
Total drag per blade = integral of D'(r) dr over the blade.
"""
import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from cd_lookup import cd_from_aoa

RHO = 1.225      # air density [kg/m^3], ISA sea level
N_BLADES = 2     # set to your propeller's blade count
V_COL = "tip_speed_m_s"   # <-- rename to the local-velocity column in velocities.py

# Import the results dataframe from velocities.py without its console printout
with redirect_stdout(io.StringIO()):
    from velocities import df as vel

geometry = pd.read_csv("blade_geometry_m.csv").reset_index(names="section")
df = vel.merge(
    geometry[["section", "r_begin_m", "r_end_m", "delta_r_m", "chord_m"]],
    on="section",
)

# Section area, Cd, section drag, drag per unit span
df["S_m2"] = df["chord_m"] * df["delta_r_m"]
df["cd"] = cd_from_aoa(df["aoa_deg"], df["pitch_deg"])
df["Drag_N"] = 0.5 * RHO * df[V_COL] ** 2 * df["S_m2"] * df["cd"]
df["drag_per_span_N/m"] = df["Drag_N"] / df["delta_r_m"]


def integrate_drag(case):
    """Midpoint-rule integral of D'(r) over each section's [r_begin, r_end].
    Equal to the sum of section drags. NaN if any section has no Cd."""
    return case["Drag_N"].sum(min_count=len(case))


# One subplot per (rpm, V0) case
cases = list(df.groupby(["rpm", "vzero"]))
fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
summary = []

for ax, ((rpm, v0), case) in zip(axes.flat, cases):
    case = case.sort_values("r_mid_m")
    total = integrate_drag(case)
    summary.append({"rpm": rpm, "vzero": v0,
                    "drag_per_blade_N": total,
                    "drag_total_N": total * N_BLADES})

    # Piecewise-constant D'(r): each section's value held over [r_begin, r_end]
    edges = np.append(case["r_begin_m"].to_numpy(), case["r_end_m"].iloc[-1])
    vals = case["drag_per_span_N/m"].to_numpy()
    ax.stairs(vals, edges, fill=True, alpha=0.3, color="C0")
    ax.stairs(vals, edges, color="C0", lw=1.5)
    ax.plot(case["r_mid_m"], vals, "o", color="C0", ms=4)

    if np.isnan(total):
        n_missing = case["cd"].isna().sum()
        text = f"Cd missing for {n_missing}/{len(case)} sections\n(AoA outside table)"
    else:
        text = f"Per blade: {total:.5f} N\n{N_BLADES} blades: {total * N_BLADES:.5f} N"
    ax.text(0.03, 0.95, text, transform=ax.transAxes, va="top",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85))

    ax.set_title(f"{rpm} rpm, $V_0$ = {v0} m/s")
    ax.grid(True, alpha=0.3)

for ax in axes[-1]:
    ax.set_xlabel("Radius r [m]")
for ax in axes[:, 0]:
    ax.set_ylabel("Drag per unit span D' [N/m]")

fig.suptitle(r"Spanwise drag distribution, shaded area = $\int D'\,dr$ = total drag per blade")
fig.tight_layout()
fig.savefig("drag_distribution.png", dpi=200)

summary = pd.DataFrame(summary)
print(df[["section", "rpm", "vzero", "r_mid_m", "chord_m", "delta_r_m",
          "S_m2", "cd", "Drag_N", "drag_per_span_N/m"]].to_string(index=False))
print("\n", summary.round(3).to_string(index=False))

df.to_csv("drag_out.csv", index=False)
plt.show()