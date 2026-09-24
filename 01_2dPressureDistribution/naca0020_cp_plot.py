"""
Plot of -Cp versus x/c for a NACA 0020 airfoil (experimental data).
"""

import numpy as np
import matplotlib.pyplot as plt

# Set to True for smooth curves through the points (needs scipy).
# PCHIP interpolation is used because, unlike Excel's smoothing,
# it does not overshoot between data points.
SMOOTH = True

# ---------------- Experimental data ----------------
# Upper side
x_upper = np.array([0.034920635, 0.096825397, 0.187301587,
                    0.317460317, 0.498412698, 0.688888889])
cp_upper = np.array([-0.666666667, -1.5, -1.333333333,
                     -1.083333333, -0.75, -0.416666667])

# Lower side
x_lower = np.array([0.061904762, 0.138095238, 0.234920635,
                    0.406349206, 0.592063492, 0.784126984])
cp_lower = np.array([0.333333333, -0.25, -0.416666667,
                     -0.5, -0.416666667, -0.333333333])

# ---------------- Plot ----------------
fig, ax = plt.subplots(figsize=(9, 5.5))


def plot_side(x, cp, label, color, marker):
    ax.plot(x, -cp, linestyle="none", marker=marker, color=color,
            markersize=7, label=label)
    if SMOOTH:
        from scipy.interpolate import PchipInterpolator
        xs = np.linspace(x.min(), x.max(), 300)
        ax.plot(xs, -PchipInterpolator(x, cp)(xs), color=color, linewidth=1.8)
    else:
        ax.plot(x, -cp, color=color, linewidth=1.2)

#### I swapped the upper and lower sides because Claude did it incorrectly.
plot_side(x_upper, cp_upper, r"Lower side, $C_{p,l}$", "tab:blue", "o")
plot_side(x_lower, cp_lower, r"Upper side, $C_{p,u}$", "tab:red", "x")

#### CUSTOM %%%%
# ---------------- Pressure difference (lift distribution) ----------------
x_common = np.linspace(max(x_upper.min(), x_lower.min()),
                       min(x_upper.max(), x_lower.max()), 300)

if SMOOTH:
    from scipy.interpolate import PchipInterpolator
    cpu = PchipInterpolator(x_upper, cp_upper)(x_common)
    cpl = PchipInterpolator(x_lower, cp_lower)(x_common)
else:
    cpu = np.interp(x_common, x_upper, cp_upper)
    cpl = np.interp(x_common, x_lower, cp_lower)

dcp = cpl - cpu                                       # positive = net upward pressure

# Trapezoidal integration over the overlapping range only
cl_partial = np.sum(0.5 * (dcp[1:] + dcp[:-1]) * np.diff(x_common))
print(f"Partial c_l (x/c = {x_common[0]:.3f} to {x_common[-1]:.3f}): {cl_partial:.3f}")

plot_difference=False

if plot_difference:
	ax.plot(x_common, dcp, color="tab:green", linewidth=2, linestyle="--",
        	label=rf"$\Delta C_p = C_{{p,l}} - C_{{p,u}}$")
	ax.fill_between(x_common, 0, dcp, color="tab:green", alpha=0.15)
####


ax.axhline(0, color="black", linewidth=0.8)
ax.set_xlim(0, 1)
ax.set_xlabel(r"$x/c$ [-]", fontsize=12)
ax.set_ylabel(r"$-C_p$ [-]", fontsize=12)
ax.set_title(r"Pressure distribution, NACA 0020, $\alpha=-5 ^{\circ}$", fontsize=13)
ax.grid(True, which="major", linestyle="--", alpha=0.6)
ax.minorticks_on()
ax.grid(True, which="minor", linestyle=":", alpha=0.3)
ax.legend(fontsize=11)

fig.tight_layout()

# ---------------- NACA 0020 outline (background, true scale) ----------------
t = 0.20                                              # max thickness / chord
xa = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 200)))   # cosine spacing: dense at LE/TE
yt = 5 * t * (0.2969*np.sqrt(xa) - 0.1260*xa - 0.3516*xa**2
              + 0.2843*xa**3 - 0.1015*xa**4)

ax2 = ax.twinx()                                      # separate axis for the geometry
ax2.fill_between(xa, -yt, yt, color="lightgray", alpha=0.5)
ax2.plot(xa, yt, color="gray", linewidth=1)
ax2.plot(xa, -yt, color="gray", linewidth=1)

# Pressure tap locations on the surface
ax2.plot(x_upper, np.interp(x_upper, xa, yt), "o", color="tab:blue", markersize=4)
ax2.plot(x_lower, -np.interp(x_lower, xa, yt), "x", color="tab:red", markersize=4)

# Match vertical and horizontal scale so the airfoil isn't distorted
pos = ax.get_position()
fig_w, fig_h = fig.get_size_inches()
x_span = ax.get_xlim()[1] - ax.get_xlim()[0]
y_span = x_span * (pos.height * fig_h) / (pos.width * fig_w)

y_min,y_max = ax.get_ylim()
f = (0 - y_min) / (y_max - y_min)
ax2.set_ylim(-f * y_span, (1-f)*y_span)

#ax2.set_ylim(-0.25 * y_span, 0.75 * y_span)           # chord line ~25% up from the bottom
ax2.set_yticks([])

# Keep the Cp curves drawn on top of the airfoil
ax.set_zorder(ax2.get_zorder() + 1)
ax.patch.set_visible(False)

fig.savefig("naca0020_cp.png", dpi=300)
plt.show()
