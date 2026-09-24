import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
P_ATM = 103020.0      # [Pa]  <-- REPLACE with your measured atmospheric pressure
AOA_DEG = -5          # only used for the title
ARROW_LENGTH = 0.15   # length (in x/c units) of the largest arrow

# Which tap set lies on which surface (swap if your setup is the other way round)
ODD_ON_UPPER = False  # False -> odd taps on the lower surface, even taps on the upper

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
# NACA 0020 geometry (symmetric, t = 20 % of chord)
# ---------------------------------------------------------------
def naca00xx_thickness(x, t=0.20):
    """Half-thickness y_t/c at position x/c (closed trailing edge)."""
    return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2
                    + 0.2843 * x**3 - 0.1036 * x**4)

x_prof = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 300)))  # cosine spacing
y_prof = naca00xx_thickness(x_prof)

# Tap positions on the surface
y_up = naca00xx_thickness(xc_up)
y_lo = -naca00xx_thickness(xc_lo)

# ---------------------------------------------------------------
# Arrows: vertical, length proportional to (p - p_atm), positive = up
# ---------------------------------------------------------------
dp_up = p_up - P_ATM
dp_lo = p_lo - P_ATM
scale = ARROW_LENGTH / max(np.abs(dp_up).max(), np.abs(dp_lo).max())

fig, ax = plt.subplots(figsize=(11, 5))

ax.fill_between(x_prof, y_prof, -y_prof, color="lightgrey", zorder=1)
ax.plot(x_prof, y_prof, "k", lw=1.2, zorder=2)
ax.plot(x_prof, -y_prof, "k", lw=1.2, zorder=2)

arrow_kw = dict(angles="xy", scale_units="xy", scale=1, width=0.004, zorder=3)
ax.quiver(xc_up, y_up, np.zeros_like(dp_up), dp_up * scale,
          color="tab:orange", label="Upper surface", **arrow_kw)
ax.quiver(xc_lo, y_lo, np.zeros_like(dp_lo), dp_lo * scale,
          color="tab:blue", label="Lower surface", **arrow_kw)

ax.plot(xc_up, y_up, "o", color="tab:orange", ms=5, zorder=4)
ax.plot(xc_lo, y_lo, "o", color="tab:blue", ms=5, zorder=4)

# Annotate p - p_atm at each tap
for x, y, dp in zip(xc_up, y_up, dp_up):
    ax.annotate(f"{dp:+.0f}", (x, y + dp * scale), textcoords="offset points",
                xytext=(0, 6 if dp >= 0 else -12), ha="center", fontsize=8,
                color="tab:orange")
for x, y, dp in zip(xc_lo, y_lo, dp_lo):
    ax.annotate(f"{dp:+.0f}", (x, y + dp * scale), textcoords="offset points",
                xytext=(0, 6 if dp >= 0 else -12), ha="center", fontsize=8,
                color="tab:blue")

# Reference arrow for scale (100 Pa)
ref_dp = 100
ax.quiver([0.95], [0.05], [0], [ref_dp * scale], color="k", **arrow_kw)
ax.text(0.97, 0.05 + ref_dp * scale / 2, f"{ref_dp} Pa", va="center", fontsize=9)

ax.set_aspect("equal")
ax.set_xlim(-0.05, 1.1)
ax.set_ylim(-0.35, 0.35)
ax.set_xlabel("x/c [-]")
ax.set_ylabel("y/c [-]")
ax.set_title(f"NACA 0020, AoA = {AOA_DEG}°  —  arrows: p − p_atm "
             f"(p_atm = {P_ATM:.0f} Pa)")
ax.grid(True, alpha=0.3)
ax.legend(loc="lower right")

plt.tight_layout()
plt.show()
