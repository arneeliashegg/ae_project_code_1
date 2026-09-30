import pandas as pd
import numpy as np
from cl_lookup import cl_from_aoa

geometry = pd.read_csv("blade_geometry_m.csv")
rpm_v = pd.read_csv("rpm_vzero.csv")
cl_table = pd.read_csv("cl_vs_aoa_pitch.csv")

# One pitch angle per section, rows in the same order as blade_geometry_m.csv
geometry["pitch_deg"] = cl_table["pitch_deg"]

# rpm -> rps
rpm_v["rps"] = rpm_v["rpm"] / 60

def omega(rps):
    return 2 * np.pi * rps                      # rad/s

def tip_speed(v, rps, r):
    return np.sqrt(v**2 + (omega(rps) * r)**2)  # resultant velocity at radius r

# Every section paired with every (rps, vzero) case: 10 sections x 6 cases = 60 rows
df = geometry[["r_mid_m", "pitch_deg"]].reset_index(names="section").merge(
    rpm_v[["rpm", "rps", "vzero"]], how="cross"
)

df["omega_rad_s"] = omega(df["rps"])
df["tip_speed_m_s"] = tip_speed(df["vzero"], df["rps"], df["r_mid_m"])

# Flow angle phi: axial velocity over rotational velocity (omega * r)
df["phi_rad"] = np.arctan(df["vzero"] / (df["omega_rad_s"] * df["r_mid_m"]))
df["phi_deg"] = np.degrees(df["phi_rad"])

# Angle of attack
df["aoa_deg"] = df["pitch_deg"] - df["phi_deg"]

# Lift coefficient (NaN where AoA is outside the table's -6..2 deg range)
df["cl"] = cl_from_aoa(df["aoa_deg"], df["pitch_deg"])

print(df.to_string(index=False))

# Optional: wide view, one row per section, one column per (rps, vzero) case
wide = df.pivot_table(index=["section", "r_mid_m"],
                      columns=["rps", "vzero"],
                      values="tip_speed_m_s")
print("\n", wide.round(2))

df.to_csv("velocities_out.csv", index=False)