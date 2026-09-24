import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
AOA_DEG = -5          # only used for the title
ARROW_LENGTH = 0.25   # length (in x/c units) of the largest arrow
ODD_ON_UPPER = False  # False -> odd taps on the lower surface, even taps on the upper
# (p_atm cancels out in p_upper - p_lower, so it is not needed here)

# ---------------------------------------------------------------
# Data
# ---------------------------------------------------------------
xc_odd = np.array([0.034921, 0.096825, 0.187302, 0.31746, 0.498413, 0.688889])
p_odd = np.array([102862.7, 102666.6, 102705.8, 102764.6, 102843.1, 102921.5])

xc_even = np.array([0.061905, 0.138095, 0.234921, 0.406349, 0.592063, 0.784127])
p_even = np.array([103098.1, 102921.5, 102901.9, 102901.9, 102921.5, 102941.2])

if ODD_ON_UPPER:
    xc_up, p_up, xc_lo, p_lo = xc_odd, p_odd, xc_even, p_even
else:
    xc_up, p_up, xc_lo, p_lo = xc_even, p_even, xc_odd, p_odd

# ---------------------------------------------------------------
# Upper and lower taps sit at different x/c, so interpolate both
# surfaces onto a common set of stations (all tap locations that lie
# inside the range covered by BOTH surfaces -> no extrapolation).
# ---------------------------------------------------------------
x_min = max(xc_up.min(), xc_lo.min())
x_max = min(xc_up.max(), xc_lo.max())
x_all = np.union1d(xc_up, xc_lo)
xc = x_all[(x_all >= x_min) & (x_all <= x_max)]

p_up_i = np.interp(xc, xc_up, p_up)
p_lo_i = np.interp(xc, xc_lo, p_lo)
dp = p_up_i - p_lo_i          # p_upper - p_lower

# ---------------------------------------------------------------
# NACA 0020 geometry
# ---------------------------------------------------------------
def naca00xx_thickness(x, t=0.20):
    return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2
                    + 0.2843 * x**3 - 0.1036 * x**4)

x_prof = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 300)))
y_prof = naca00xx_thickness(x_prof)

# ---------------------------------------------------------------
# Plot: arrows from the chord line (y = 0), positive dp = up
# ---------------------------------------------------------------
scale = ARROW_LENGTH / np.abs(dp).max()

fig, ax = plt.subplots(figsize=(11, 5))

ax.fill_between(x_prof, y_prof, -y_prof, color="lightgrey", zorder=1)
ax.plot(x_prof, y_prof, "k", lw=1.2, zorder=2)
ax.plot(x_prof, -y_prof, "k", lw=1.2, zorder=2)
ax.plot([0, 1], [0, 0], "k--", lw=0.8, zorder=2)   # chord line

arrow_kw = dict(angles="xy", scale_units="xy", scale=1, width=0.004, zorder=3)
ax.quiver(xc, np.zeros_like(xc), np.zeros_like(dp), dp * scale,
          color="tab:red", label=r"$p_{upper} - p_{lower}$", **arrow_kw)
ax.plot(xc, np.zeros_like(xc), "o", color="tab:red", ms=4, zorder=4)

for x, d in zip(xc, dp):
    ax.annotate(f"{d:+.0f}", (x, d * scale), textcoords="offset points",
                xytext=(0, 6 if d >= 0 else -12), ha="center", fontsize=8,
                color="tab:red")

# Reference arrow for scale (100 Pa)
ref_dp = 100
ax.quiver([0.95], [0.05], [0], [ref_dp * scale], color="k", **arrow_kw)
ax.text(0.97, 0.05 + ref_dp * scale / 2, f"{ref_dp} Pa", va="center", fontsize=9)

ax.set_aspect("equal")
ax.set_xlim(-0.05, 1.1)
ax.set_ylim(-0.35, 0.35)
ax.set_xlabel("x/c [-]")
ax.set_ylabel("y/c [-]")
ax.set_title(f"NACA 0020, AoA = {AOA_DEG}°  —  pressure difference "
             r"$p_{upper} - p_{lower}$")
ax.grid(True, alpha=0.3)
ax.legend(loc="lower right")

plt.tight_layout()
plt.show()
