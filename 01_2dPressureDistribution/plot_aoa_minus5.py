import matplotlib.pyplot as plt

# Dataset 1: odd-numbered taps (1, 3, 5, ..., 11)
taps_odd = [1, 3, 5, 7, 9, 11]
xc_odd = [0.034921, 0.096825, 0.187302, 0.31746, 0.498413, 0.688889]
p_odd = [102862.7, 102666.6, 102705.8, 102764.6, 102843.1, 102921.5]

# Dataset 2: even-numbered taps (2, 4, 6, ..., 12)
taps_even = [2, 4, 6, 8, 10, 12]
xc_even = [0.061905, 0.138095, 0.234921, 0.406349, 0.592063, 0.784127]
p_even = [103098.1, 102921.5, 102901.9, 102901.9, 102921.5, 102941.2]

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(xc_odd, p_odd, marker="v", linestyle="-", color="tab:blue",
        label="Lower Surface")
ax.plot(xc_even, p_even, marker="^", linestyle="-", color="tab:orange",
        label="Upper Surface")

# Optional: label each point with its tap number
for n, x, p in zip(taps_odd, xc_odd, p_odd):
    ax.annotate(str(n), (x, p), textcoords="offset points", xytext=(0, -14),
                ha="center", fontsize=8, color="tab:blue")
for n, x, p in zip(taps_even, xc_even, p_even):
    ax.annotate(str(n), (x, p), textcoords="offset points", xytext=(0, 7),
                ha="center", fontsize=8, color="tab:orange")

ax.set_title("AoA −5°")
ax.set_xlabel("x/c [-]")
ax.set_ylabel("Pressure [Pa]")
ax.set_xlim(0, 0.9)
ax.grid(True, alpha=0.4)
ax.legend()

plt.tight_layout()
plt.show()
