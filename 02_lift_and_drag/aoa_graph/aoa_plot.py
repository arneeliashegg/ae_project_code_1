import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("aoa-cl.csv")

# ---------------- Experimental data ----------------
## Designate which taps belong to upper/lower side
aoa=np.array([])
cl=np.array([])

for r,no in enumerate(df["aoa"]):
    aoa=np.append(aoa, no)
    cl=np.append(cl, df["cl"].iloc[r])
    
print(aoa)
print(cl)

fig, ax = plt.subplots(figsize=(9, 5.5))


def plot_side(x, cp, label, color, marker):
    ax.plot(x, cp, linestyle="none", marker=marker, color=color,
            markersize=7, label=label)

    ax.plot(x, cp, color=color, linewidth=1.2)


plot_side(aoa, cl, r"1", "tab:red", "x")

### MAIN PLOT

ax.axhline(0, color="black", linewidth=0.8)
#ax.set_xlim(0, 1)
ax.set_xlabel(r"$\alpha$ [\circ]", fontsize=12)
ax.set_ylabel(r"$C_l$ [-]", fontsize=12)
ax.set_title(r"$C_l$ - $\alpha$", fontsize=13)
ax.grid(True, which="major", linestyle="--", alpha=0.6)
ax.minorticks_on()
ax.grid(True, which="minor", linestyle=":", alpha=0.3)
ax.legend(fontsize=11)

fig.tight_layout()

ax.patch.set_visible(False)

fig.savefig(f"aoa-cl.png", dpi=300)
plt.show()

