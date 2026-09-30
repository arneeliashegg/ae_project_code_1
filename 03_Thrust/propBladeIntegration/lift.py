"""Lift per blade section and total blade lift via numerical integration.

Uses velocities.py (unchanged) for V_local, AoA and Cl.
L_i  = 0.5 * rho * V_local^2 * S_i * Cl_i,   S_i = chord_i * delta_r_i
L'_i = L_i / delta_r_i  (lift per unit span, N/m)
Total lift per blade = integral of L'(r) dr over the blade.
"""
import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RHO = 1.225      # air density [kg/m^3], ISA sea level
N_BLADES = 2     # set to your propeller's blade count

# Import the results dataframe from velocities.py without its console printout
with redirect_stdout(io.StringIO()):
    from velocities import df as vel

geometry = pd.read_csv("blade_geometry_m.csv").reset_index(names="section")
df = vel.merge(geometry[["section", "r_begin_m", "r_end_m", "delta_r_m", "chord_m"]],
               on="section")

# Section area, section lift, lift per unit span
df["S_m2"] = df["chord_m"] * df["delta_r_m"]
df["lift_N"] = 0.5 * RHO * df["tip_speed_m_s"]**2 * df["S_m2"] * df["cl"]
df["lift_per_span_N_m"] = df["lift_N"] / df["delta_r_m"]


def integrate_lift(case):
    """Midpoint-rule integral of L'(r) over each section's [r_begin, r_end].
    Equal to the sum of section lifts. NaN if any section has no Cl."""
    return (case["lift_per_span_N_m"] * case["delta_r_m"]).sum(min_count=len(case))


# One subplot per (rpm, V0) case
cases = list(df.groupby(["rpm", "vzero"]))
fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
summary = []

for ax, ((rpm, v0), case) in zip(axes.flat, cases):
    case = case.sort_values("r_mid_m")
    total = integrate_lift(case)
    summary.append({"rpm": rpm, "vzero": v0,
                    "lift_per_blade_N": total, "lift_total_N": total * N_BLADES})

    # Piecewise-constant L'(r): each section's value held over [r_begin, r_end]
    edges = np.append(case["r_begin_m"].to_numpy(), case["r_end_m"].iloc[-1])
    vals = case["lift_per_span_N_m"].to_numpy()
    ax.stairs(vals, edges, fill=True, alpha=0.3, color="C0")
    ax.stairs(vals, edges, color="C0", lw=1.5)
    ax.plot(case["r_mid_m"], vals, "o", color="C0", ms=4)

    if np.isnan(total):
        n_missing = case["cl"].isna().sum()
        text = f"Cl missing for {n_missing}/{len(case)} sections\n(AoA outside table)"
    else:
        text = f"Per blade: {total:.2f} N\n{N_BLADES} blades: {total * N_BLADES:.2f} N"
    ax.text(0.03, 0.95, text, transform=ax.transAxes, va="top",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85))

    ax.set_title(f"{rpm} rpm, $V_0$ = {v0} m/s")
    ax.grid(True, alpha=0.3)

for ax in axes[-1]:
    ax.set_xlabel("Radius r [m]")
for ax in axes[:, 0]:
    ax.set_ylabel("Lift per unit span L' [N/m]")

fig.suptitle(r"Spanwise lift distribution, shaded area = $\int L'\,dr$ = total lift per blade")
fig.tight_layout()
fig.savefig("lift_distribution.png", dpi=200)

summary = pd.DataFrame(summary)
print(df[["section", "rpm", "vzero", "r_mid_m", "chord_m", "delta_r_m",
          "S_m2", "cl", "lift_N", "lift_per_span_N_m"]].to_string(index=False))
print("\n", summary.round(3).to_string(index=False))

df.to_csv("lift_out.csv", index=False)
plt.show()
