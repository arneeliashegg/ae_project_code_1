import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

files=[("minusfive.csv", "-5"), ("zero.csv","0"), ("five.csv", "5"), ("fifteen.csv", "15"), ("twentyNew.csv","20"), ("twentyfiveNew.csv", 25)]
n=3
df = pd.read_csv(files[n][0])

#print(df)
## Toggles
plot_difference=False

# ---------------- Experimental data ----------------
## Designate which taps belong to upper/lower side
upper_taps=[2,4,6,8,10,12]
lower_taps=[1,3,5,7,9,11]

upper_taps_x=np.array([])
upper_taps_cp=np.array([])

lower_taps_x=np.array([])
lower_taps_cp=np.array([])

for r,no in enumerate(df["No"]):
    if no in upper_taps:
        upper_taps_x = np.append(upper_taps_x, df["x/c"].iloc[r])
        upper_taps_cp = np.append(upper_taps_cp, df["cp"].iloc[r])
    elif no in lower_taps:
        lower_taps_x = np.append(lower_taps_x, df["x/c"].iloc[r])
        lower_taps_cp = np.append(lower_taps_cp, df["cp"].iloc[r])

print(upper_taps_x)
print(upper_taps_cp)

"""
TODO: Create a function which can read the spreadsheets, making this a generalizable process.

# Lower side
x_lower = np.array([0.034920635, 0.096825397, 0.187301587,
                    0.317460317, 0.498412698, 0.688888889])
cp_lower = np.array([-0.666666667, -1.5, -1.333333333,
                     -1.083333333, -0.75, -0.416666667])

# Upper side
x_upper = np.array([0.061904762, 0.138095238, 0.234920635,
                    0.406349206, 0.592063492, 0.784126984])
cp_upper = np.array([0.333333333, -0.25, -0.416666667,
                     -0.5, -0.416666667, -0.333333333])
"""


# ---------------- Plot ----------------
fig, ax = plt.subplots(figsize=(9, 5.5))


def plot_side(x, cp, label, color, marker):
    ax.plot(x, cp, linestyle="none", marker=marker, color=color,
            markersize=7, label=label)

    ax.plot(x, cp, color=color, linewidth=1.2)


plot_side(upper_taps_x, upper_taps_cp, r"Upper side, $C_{p,u}$", "tab:blue", "o")
plot_side(lower_taps_x, lower_taps_cp, r"Lower side, $C_{p,u}$", "tab:red", "x")

#### CUSTOM %%%%
# ---------------- Pressure difference ----------------
x_common = np.linspace(max(upper_taps_x.min(), lower_taps_x.min()),
                       min(upper_taps_x.max(), lower_taps_x.max()), 300)

# upper pressure coefficient distribution
cpu = np.interp(x_common, upper_taps_x, upper_taps_cp)

# lower pressure coefficient distribution
cpl = np.interp(x_common, lower_taps_x, lower_taps_cp)

# Difference in interpolated pressure coefficients
dcp = cpl - cpu

# Trapezoidal integration over the overlapping range only
cl_partial = np.sum(0.5 * (dcp[1:] + dcp[:-1]) * np.diff(x_common))
print(f"Partial c_l (x/c = {x_common[0]:.3f} to {x_common[-1]:.3f}): {cl_partial:.3f}")



## If the difference should be plotted
if plot_difference:
	ax.plot(x_common, dcp, color="tab:green", linewidth=2, linestyle="--",
        	label=rf"$\Delta C_p = C_{{p,l}} - C_{{p,u}}$")
	ax.fill_between(x_common, 0, dcp, color="tab:green", alpha=0.15)

### MAIN PLOT

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xlim(0, 1)
ax.set_xlabel(r"$x/c$ [-]", fontsize=12)
ax.set_ylabel(r"$c_p$ [-]", fontsize=12)
ax.set_title(f"Pressure distribution, NACA 0020, AoA={files[n][1]}", fontsize=13)
ax.grid(True, which="major", linestyle="--", alpha=0.6)
ax.minorticks_on()
ax.grid(True, which="minor", linestyle=":", alpha=0.3)
ax.legend(fontsize=11)

fig.tight_layout()

ax.patch.set_visible(False)
ax.invert_yaxis()

fig.savefig(f"figures/naca0020_{files[n]}cp.png", dpi=300)
plt.show()
