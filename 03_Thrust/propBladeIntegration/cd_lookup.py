import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_cd_table(csv_path="cd_vs_aoa.csv"):
    """Read the Cd table. Returns (pitches, aoas, cl_grid) with
    cl_grid[i, j] = Cl at pitches[i] and aoas[j], both sorted ascending."""
    df = pd.read_csv(csv_path).sort_values("pitch_deg")
    cd_cols = [c for c in df.columns if c.startswith("Cd_aoa_")]
    aoas = np.array([float(c.replace("Cd_aoa_", "")) for c in cd_cols])
    order = np.argsort(aoas)
    return (df["pitch_deg"].to_numpy(),
            aoas[order],
            df[cd_cols].to_numpy()[:, order])


PITCHES, AOAS, CD_GRID = load_cd_table()


def _interp_1d(x, xp, fp, extrapolate):
    """np.interp, but outside xp either returns NaN or extends the end slopes."""
    y = np.interp(x, xp, fp)
    lo, hi = x < xp[0], x > xp[-1]
    if extrapolate:
        y = np.where(lo, fp[0] + (x - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0]), y)
        y = np.where(hi, fp[-1] + (x - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2]), y)
    else:
        y = np.where(lo | hi, np.nan, y)
    return y


def cd_from_aoa(aoa_deg, pitch_deg, extrapolate=False):
    """Cl for a given angle of attack [deg] at a blade section with the given pitch [deg].

    Linear interpolation in AoA, then in pitch (bilinear). Works on scalars,
    numpy arrays, or pandas Series (element-wise).

    extrapolate=False -> NaN outside the tabulated AoA range (default, so
                         out-of-range points are visible rather than silently clamped)
    extrapolate=True  -> linear extension of the nearest segment (ignores stall!)
    """
    aoa = np.atleast_1d(np.asarray(aoa_deg, dtype=float))
    pitch = np.atleast_1d(np.asarray(pitch_deg, dtype=float))
    aoa, pitch = np.broadcast_arrays(aoa, pitch)

    # Step 1: Cl at the requested AoA for every tabulated pitch -> shape (n_pitch, n_points)
    cd_at_aoa = np.array([_interp_1d(aoa, AOAS, row, extrapolate) for row in CD_GRID])

    # Step 2: interpolate across pitch for each point
    out = np.empty(aoa.shape)
    for k in range(aoa.size):
        out.flat[k] = _interp_1d(pitch.flat[k], PITCHES, cd_at_aoa[:, k], extrapolate=False)

    if isinstance(aoa_deg, pd.Series):
        return pd.Series(out, index=aoa_deg.index)
    return out.item() if out.size == 1 else out


def plot_cd_vs_pitch(save_path="cd_vs_pitch.png"):
    fig, ax = plt.subplots(figsize=(9, 6))
    for j, a in enumerate(AOAS):
        ax.plot(PITCHES, CD_GRID[:, j], marker="o", label=f"AoA = {a}°")
    ax.invert_xaxis()
    ax.set_xlabel(r"$\beta$ [$^\circ$]")
    ax.set_ylabel(r"$C_d$ [-]")
    ax.set_title(r"$C_d$ vs $\beta$ for each $\alpha$")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Angle of attack")
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.show()


if __name__ == "__main__":
    print(cd_from_aoa(0.4, 38.51))          # exact table value -> 0.538974
    print(cd_from_aoa(-2.0, 38.51))         # between -2.8 and -1.2
    print(cd_from_aoa(5.0, 20.10))          # out of range -> nan
    print(cd_from_aoa(5.0, 20.10, extrapolate=False))
    plot_cd_vs_pitch()
