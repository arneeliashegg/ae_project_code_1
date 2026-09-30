import io
import pandas as pd
import matplotlib.pyplot as plt

# Point this at your CSV file, or leave as None to use the embedded data below
CSV_PATH = None  # e.g. "cl_data.csv"

DATA = """pitch_deg,Cl_aoa_-6.0,Cl_aoa_-4.4,Cl_aoa_-2.8,Cl_aoa_-1.2,Cl_aoa_0.4,Cl_aoa_2.0
38.51,-0.220196,-0.004853,0.160581,0.352234,0.538974,0.728673
30.06,0.007624,0.18093,0.371484,0.559937,0.744482,0.929433
24.45,0.108406,0.297784,0.485087,0.670612,0.854194,1.035646
20.10,0.141715,0.336768,0.530048,0.717627,0.902468,1.085452
17.66,0.162542,0.325107,0.54437,0.743635,0.918124,1.087204
15.87,0.194847,0.314652,0.489242,0.714794,0.890209,1.076879
14.62,0.210482,0.33788,0.474175,0.679349,0.88247,1.057069
13.76,0.18279,0.312447,0.458656,0.649325,0.85828,1.04011
13.25,0.170245,0.303045,0.454028,0.639559,0.849436,1.032581
12.97,0.162948,0.297765,0.452957,0.642476,0.845508,1.030828
"""

df = pd.read_csv(CSV_PATH) if CSV_PATH else pd.read_csv(io.StringIO(DATA))
df = df.sort_values("pitch_deg")

fig, ax = plt.subplots(figsize=(9, 6))

for col in df.columns[1:]:
    aoa = col.replace("Cl_aoa_", "")
    ax.plot(df["pitch_deg"], df[col], marker="o", label=f"AoA = {aoa}°")

ax.set_xlabel("Pitch angle [deg]")
ax.set_ylabel(r"$C_l$ [-]")
ax.set_title(r"$C_l$ vs pitch angle for each angle of attack")
ax.grid(True, alpha=0.3)
ax.legend(title="Angle of attack")
fig.tight_layout()

fig.savefig("cl_vs_pitch.png", dpi=200)
plt.show()