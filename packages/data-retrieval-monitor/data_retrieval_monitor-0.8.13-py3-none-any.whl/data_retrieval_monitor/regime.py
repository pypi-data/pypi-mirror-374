#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regime Analysis Pipeline — FULL (outputs -> ./output2)

What it does
------------
1) Reads factor PRICE LEVELS and 4 INDICATORS (CSV with date index).
2) Computes LOG RETURNS; shifts indicators by +2 business days (no leakage).
3) Sign-based analysis per indicator (Positive vs Negative):
   - Annualized Mean, Volatility, Sharpe
   - Professional heatmaps
4) Systematic regime models on ALL 4 indicators (scaled + PCA):
   - KMeans (raw), Gaussian Mixture (raw), Bayesian GMM (raw),
   - Agglomerative (on PCA), KMeans (on PCA), Spectral Clustering (on PCA),
   - Optional HMM (raw indicators) if hmmlearn is installed
5) Per-regime factor performance (Mean, Vol, Sharpe) + professional heatmaps
6) Exhibit-4-style multi-row timeline (colored timepoints by regimes)
7) Factor time series with translucent regime bands (midpoint method — no gaps)
8) Dummy variables for every model’s regimes + indicator sign dummies
9) Optional CHANGePOINT DETECTION (via ruptures): Binseg / PELT / KernelCPD

CSV formats expected
--------------------
- levels.csv:  date index in first column; remaining columns are factor PRICE LEVELS
- indicators.csv: date index; EXACTLY 4 indicator columns

All outputs are written to ./output2
"""

import os
import math
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import ListedColormap

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture

# Optional HMM
try:
    from hmmlearn import hmm
    HMM_AVAILABLE = True
except Exception:
    HMM_AVAILABLE = False

# Optional changepoint detection
try:
    import ruptures as rpt
    CPD_AVAILABLE = True
except Exception:
    CPD_AVAILABLE = False


# ============================ CONFIG ============================
LEVELS_CSV = "levels.csv"           # price levels (date index, factor columns)
INDICATORS_CSV = "indicators.csv"   # 4 indicators (date index, 4 columns)
OUTPUT_DIR = "output2"              # <— per your request

# Models / embeddings
N_CLUSTERS = 4
PCA_COMPONENTS = 3
SPECTRAL_KNN = 15  # for spectral clustering nearest-neighbor affinity

# Plotting presets
TIMELINE_ROWS = 5                    # rows in Exhibit-4 style timeline
BANDS_ALPHA = 0.18                   # opacity of regime bands on time series

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================ UTILITIES ============================
def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def infer_periods_per_year(dates_index: pd.DatetimeIndex) -> int:
    """Infer annualization factor from timestamp spacing."""
    if len(dates_index) < 3:
        return 252
    diffs = np.diff(dates_index.values.astype("datetime64[ns]")).astype("timedelta64[D]").astype(int)
    median_days = np.median(diffs)
    if median_days <= 2:   # ~daily business days
        return 252
    elif median_days <= 10:
        return 52          # weekly
    elif median_days <= 40:
        return 12          # monthly
    else:
        return 1

def annualized_stats(returns_df: pd.DataFrame, ann_factor: int) -> dict:
    """Annualized mean, vol, sharpe for each column."""
    mu = returns_df.mean() * ann_factor
    vol = returns_df.std() * math.sqrt(ann_factor)
    sharpe = (returns_df.mean() / returns_df.std()) * math.sqrt(ann_factor)
    return {"mean": mu, "vol": vol, "sharpe": sharpe}

def save_table(df: pd.DataFrame, name: str):
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path)
    return path

# -------------------- Pretty plotting helpers --------------------
def _regime_palette(n):
    # Distinct, readable colors (10-cycle if needed)
    base = plt.get_cmap("tab10")
    return [base(i % 10) for i in range(n)]

def _format_pct(x, pos):
    return f"{x*100:.0f}%"

def professional_heatmap(df, title, fname=None, fmt=".2%", center_zero=True,
                         cbar_label=None):
    """
    Clean, presentation-ready heatmap:
    - white gridlines
    - bold title, tight layout
    - optional zero-centering (good for Sharpe/alpha)
    - percent formatting default
    """
    values = df.values.astype(float)
    if center_zero:
        vmax = np.nanmax(np.abs(values))
        vmin = -vmax
        cmap = "coolwarm"
    else:
        vmin, vmax = np.nanmin(values), np.nanmax(values)
        cmap = "viridis"

    fig_h = max(3.8, 0.34 * len(df))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    im = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)

    # gridlines
    ax.set_xticks(np.arange(values.shape[1]+1)-0.5, minor=True)
    ax.set_yticks(np.arange(values.shape[0]+1)-0.5, minor=True)
    ax.grid(which="minor", color="w", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_xticks(np.arange(values.shape[1]))
    ax.set_yticks(np.arange(values.shape[0]))
    ax.set_xticklabels(df.columns, rotation=0)
    ax.set_yticklabels(df.index)

    # annotate cells
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val = values[i, j]
            try:
                txt = format(val, fmt)
            except Exception:
                txt = f"{val:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color="black")

    # colorbar
    formatter = FuncFormatter(_format_pct) if "%" in fmt else None
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, format=formatter)
    if cbar_label:
        cbar.set_label(cbar_label)

    ax.set_title(title, fontsize=13, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()

def plot_timeline_chunked(labels, dates, title="Regimes Through Time",
                          n_rows=5, fname=None):
    """
    Exhibit-4 style: split the full sample into n_rows horizontal strips and
    color each timepoint by regime.
    """
    labels = np.asarray(labels).ravel()
    dates = pd.to_datetime(dates)
    mask = ~pd.isna(dates)
    labels = labels[mask]
    dates = dates[mask]

    # split into contiguous chunks by time
    chunks = np.array_split(np.arange(len(dates)), n_rows)
    K = int(labels.max()) + 1
    colors = _regime_palette(K)

    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 1.2 * n_rows), sharex=False)
    if n_rows == 1:
        axes = [axes]

    for ax, idx in zip(axes, chunks):
        if len(idx) == 0:
            continue
        arr = labels[idx].reshape(1, -1)
        cmap = ListedColormap(colors[:K])
        ax.imshow(arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=K-0.5)
        ax.set_yticks([])
        # year ticks
        sub_dates = dates[idx]
        years = sorted({d.year for d in sub_dates})
        step = max(1, len(years)//8)
        ticks, labs = [], []
        for y in years[::step]:
            j = idx[np.argmax(sub_dates.year == y)]
            ticks.append(j - idx[0])
            labs.append(str(y))
        ax.set_xticks(ticks)
        ax.set_xticklabels(labs)
        # remove borders
        for spine in ax.spines.values():
            spine.set_visible(False)

    counts = pd.Series(labels).value_counts(normalize=True).sort_index()
    legend_handles = [
        patches.Patch(facecolor=colors[k], edgecolor="none",
                      label=f"Regime {k}, {counts.get(k,0):.0%}")
        for k in range(K)
    ]
    fig.legend(handles=legend_handles, ncol=min(4, K), loc="upper center",
               bbox_to_anchor=(0.5, 1.05))
    fig.suptitle(title, y=1.08, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()

def plot_series_with_regime_bands(dates, series, regime_labels, title=None, fname=None, alpha=BANDS_ALPHA):
    """
    Continuous shading (no white gaps): uses midpoints between timestamps as regime edges.
    """
    dates = pd.to_datetime(dates)
    s = pd.Series(series, index=dates).dropna()
    r = pd.Series(regime_labels, index=dates).reindex(s.index).ffill().bfill().astype(int)

    t = s.index.view('int64').to_numpy()  # ns since epoch
    if len(t) < 2:
        return
    mids = (t[:-1] + t[1:]) // 2
    left_edge  = t[0] - (mids[0] - t[0])        if len(mids) else t[0]
    right_edge = t[-1] + (t[-1] - mids[-1])     if len(mids) else t[-1]
    edges = np.concatenate([[left_edge], mids, [right_edge]])
    dt_edges = pd.to_datetime(edges, unit="ns")

    reg = r.to_numpy()
    K = int(reg.max()) + 1
    colors = _regime_palette(K)

    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.plot(s.index, s.values, lw=1.5, zorder=10)
    ax.set_xlim(s.index.min(), s.index.max())
    ax.grid(axis="y", alpha=0.25)

    for k in range(len(reg)):
        ax.axvspan(dt_edges[k], dt_edges[k+1],
                   facecolor=colors[reg[k]], alpha=alpha, linewidth=0)

    handles = [patches.Patch(facecolor=colors[k], alpha=alpha, edgecolor="none", label=f"Regime {k}")
               for k in range(K)]
    ax.legend(handles=handles, ncol=min(4, K), loc="upper left", frameon=False)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()


# ============================ DATA LOADING (with simulation fallback) ============================
def load_or_simulate():
    if os.path.exists(LEVELS_CSV) and os.path.exists(INDICATORS_CSV):
        levels = ensure_datetime_index(pd.read_csv(LEVELS_CSV, index_col=0))
        indicators = ensure_datetime_index(pd.read_csv(INDICATORS_CSV, index_col=0))
        return levels, indicators, True

    # Simulate realistic data (daily, 20 factors, 4 indicators)
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2017-01-03", "2024-12-31")
    n, n_assets, n_ind = len(dates), 20, 4

    t = np.arange(n)
    indicators = pd.DataFrame({
        "Ind1_Growth": 0.5*np.sin(2*np.pi*t/260) + 0.3*rng.standard_normal(n),
        "Ind2_Infl":   0.6*np.cos(2*np.pi*t/500) + 0.3*rng.standard_normal(n),
        "Ind3_Stress": 0.4*np.sin(2*np.pi*t/780 + 1.0) + 0.4*rng.standard_normal(n),
        "Ind4_Liq":    0.6*np.cos(2*np.pi*t/390 + 0.7) + 0.3*rng.standard_normal(n),
    }, index=dates)

    B = rng.normal(0, 0.1, size=(n_ind, n_assets))
    base_mu = rng.normal(0.04/252, 0.02/252, size=n_assets)
    base_sigma = rng.uniform(0.12/np.sqrt(252), 0.3/np.sqrt(252), size=n_assets)

    eps = rng.standard_normal((n, n_assets)) * base_sigma
    drift = (indicators.values @ B) / 252.0
    rets = base_mu + drift + eps
    levels = 100 * np.exp(np.cumsum(rets, axis=0))
    cols = [f"Factor_{i+1:02d}" for i in range(n_assets)]
    levels = pd.DataFrame(levels, index=dates, columns=cols)

    print(">> CSVs not found; generated a synthetic dataset to demonstrate the pipeline.")
    return levels, indicators, False


# ============================ SIGN-BASED ANALYSIS ============================
def sign_based_analysis(returns: pd.DataFrame, indicators_shifted: pd.DataFrame, ann_factor: int):
    for ind in indicators_shifted.columns:
        pos = indicators_shifted[ind] > 0
        neg = ~pos

        stats_pos = annualized_stats(returns.loc[pos], ann_factor)
        stats_neg = annualized_stats(returns.loc[neg], ann_factor)

        df_mean = pd.DataFrame({"Positive": stats_pos["mean"], "Negative": stats_neg["mean"]})
        df_vol  = pd.DataFrame({"Positive": stats_pos["vol"],  "Negative": stats_neg["vol"]})
        df_sharpe = pd.DataFrame({"Positive": stats_pos["sharpe"], "Negative": stats_neg["sharpe"]})

        save_table(df_mean, f"{ind}_mean_by_sign")
        save_table(df_vol,  f"{ind}_vol_by_sign")
        save_table(df_sharpe, f"{ind}_sharpe_by_sign")

        professional_heatmap(df_mean,   f"{ind}: Annualized Mean (Pos/Neg)",   f"{ind}_mean_heatmap",   fmt=".2%")
        professional_heatmap(df_vol,    f"{ind}: Annualized Vol (Pos/Neg)",    f"{ind}_vol_heatmap",    fmt=".2%")
        professional_heatmap(df_sharpe, f"{ind}: Sharpe (Pos/Neg)",            f"{ind}_sharpe_heatmap", fmt=".2f", center_zero=True, cbar_label="Sharpe")


# ============================ SYSTEMATIC REGIME MODELS ============================
def fit_regime_models(ind_scaled: np.ndarray, dates: pd.DatetimeIndex) -> dict:
    labels = {}

    # KMeans on indicators
    labels["kmeans_ind"] = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=0).fit_predict(ind_scaled)

    # GMM on indicators
    labels["gmm_ind"] = GaussianMixture(n_components=N_CLUSTERS, covariance_type="full", random_state=0)\
                        .fit_predict(ind_scaled)

    # Bayesian GMM (estimates component usage; N_CLUSTERS is an upper bound)
    labels["bayes_gmm_ind"] = BayesianGaussianMixture(n_components=N_CLUSTERS, covariance_type="full",
                                                      random_state=0).fit_predict(ind_scaled)

    # PCA embedding
    pca = PCA(n_components=min(PCA_COMPONENTS, ind_scaled.shape[1]))
    Xp = pca.fit_transform(ind_scaled)

    # Agglomerative on PCA
    labels["agg_pca"] = AgglomerativeClustering(n_clusters=N_CLUSTERS).fit_predict(Xp)

    # KMeans on PCA
    labels["kmeans_pca"] = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=0).fit_predict(Xp)

    # Spectral clustering using k-NN affinity on PCA space
    n_neighbors = max(2, min(SPECTRAL_KNN, Xp.shape[0]-1))
    labels["spectral_pca"] = SpectralClustering(n_clusters=N_CLUSTERS, affinity="nearest_neighbors",
                                                n_neighbors=n_neighbors,
                                                random_state=0, assign_labels="kmeans")\
                             .fit_predict(Xp)

    # Optional HMM on indicators
    if HMM_AVAILABLE:
        ghmm = hmm.GaussianHMM(n_components=N_CLUSTERS, covariance_type="full", n_iter=200, random_state=0)
        ghmm.fit(ind_scaled)
        labels["hmm_ind"] = ghmm.predict(ind_scaled)

    # Save timeline plots
    for name, lab in labels.items():
        plot_timeline_chunked(lab, dates, title=f"Highest-Probability Market Conditions — {name}",
                              n_rows=TIMELINE_ROWS, fname=f"exhibit4_{name}")

    return labels


# ============================ CHANGEPOINT DETECTION (optional) ============================
def fit_changepoint_models(ind_scaled: np.ndarray, dates: pd.DatetimeIndex, n_bkps: int = 6) -> dict:
    """
    Multivariate changepoint detection on scaled indicators.
    Returns dict of labels per date (segment IDs), one series per algorithm.
    n_bkps is the *maximum* number of breakpoints (segments = n_bkps+1).
    """
    labels = {}
    if not CPD_AVAILABLE or ind_scaled.shape[0] < 10:
        return labels

    T = ind_scaled.shape[0]
    n_bkps = max(1, min(n_bkps, T // 50))  # avoid overfitting on short samples

    # 1) Binary Segmentation (l2)
    try:
        algo = rpt.Binseg(model="l2").fit(ind_scaled)
        bkps = algo.predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels[f"cpd_binseg_{n_bkps}"] = seg
    except Exception:
        pass

    # 2) PELT (rbf) with dynamic penalty
    try:
        pen = 10.0 * np.log(T) * (ind_scaled.shape[1] ** 0.5)
        algo = rpt.Pelt(model="rbf").fit(ind_scaled)
        bkps = algo.predict(pen=pen)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels["cpd_pelt_rbf"] = seg
    except Exception:
        pass

    # 3) KernelCPD (rbf)
    try:
        algo = rpt.KernelCPD(kernel="rbf").fit(ind_scaled)
        bkps = algo.predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels[f"cpd_kernel_{n_bkps}"] = seg
    except Exception:
        pass

    # Exhibit-4 timelines for CPD
    for name, lab in labels.items():
        plot_timeline_chunked(lab, dates, title=f"Changepoint Segments — {name}",
                              n_rows=TIMELINE_ROWS, fname=f"exhibit4_{name}")
    return labels


# ============================ EVALUATION / EXPORT ============================
def per_regime_factor_stats(returns: pd.DataFrame, ann_factor: int, regime_labels: dict, dates: pd.DatetimeIndex):
    regimes_df = pd.DataFrame(regime_labels, index=dates)
    save_table(regimes_df, "regimes_by_model")

    for model_name in regimes_df.columns:
        labs = regimes_df[model_name].values
        uniq = np.unique(labs)

        out_mean   = pd.DataFrame(index=returns.columns, columns=[f"Regime {int(s)}" for s in uniq])
        out_vol    = out_mean.copy()
        out_sharpe = out_mean.copy()

        for s in uniq:
            mask = labs == s
            if mask.sum() == 0:
                continue
            stats = annualized_stats(returns.loc[mask], ann_factor)
            out_mean[f"Regime {int(s)}"]   = stats["mean"]
            out_vol[f"Regime {int(s)}"]    = stats["vol"]
            out_sharpe[f"Regime {int(s)}"] = stats["sharpe"]

        save_table(out_mean,   f"{model_name}_annualized_mean_by_regime")
        save_table(out_vol,    f"{model_name}_annualized_vol_by_regime")
        save_table(out_sharpe, f"{model_name}_sharpe_by_regime")

        professional_heatmap(out_mean,   f"{model_name}: Annualized Mean by Regime",
                             f"{model_name}_mean_heatmap",   fmt=".2%")
        professional_heatmap(out_vol,    f"{model_name}: Annualized Vol by Regime",
                             f"{model_name}_vol_heatmap",    fmt=".2%")
        professional_heatmap(out_sharpe, f"{model_name}: Sharpe by Regime",
                             f"{model_name}_sharpe_heatmap", fmt=".2f", center_zero=True, cbar_label="Sharpe")

    return regimes_df


def make_dummies(regimes_df: pd.DataFrame, indicators_shifted: pd.DataFrame) -> pd.DataFrame:
    """One-hot dummies for regimes of each model + sign dummies for indicators."""
    parts = []
    for col in regimes_df.columns:
        onehot = pd.get_dummies(regimes_df[col], prefix=f"{col}_R")
        parts.append(onehot)

    for ind in indicators_shifted.columns:
        parts.append(pd.Series((indicators_shifted[ind] > 0).astype(int), name=f"{ind}_POS"))
        parts.append(pd.Series((indicators_shifted[ind] <= 0).astype(int), name=f"{ind}_NEG"))

    dummies = pd.concat(parts, axis=1)
    save_table(dummies, "regime_and_sign_dummies")
    return dummies


# ============================ MAIN ============================
def main():
    # Load or simulate data
    levels, indicators, loaded = load_or_simulate()

    # Compute log returns from price levels
    logp = np.log(levels)
    returns = logp.diff().dropna()

    # Shift indicators by +2 days to avoid look-ahead leakage
    ind_shifted = indicators.shift(2)

    # Align & drop NaNs
    data = returns.join(ind_shifted, how="inner").dropna()
    returns_aligned = data[returns.columns]
    indicators_aligned = data[ind_shifted.columns]

    # Save bases
    save_table(returns_aligned, "returns_computed")
    save_table(indicators_aligned, "indicators_shifted_by2d")

    # Annualization factor
    ann_factor = infer_periods_per_year(returns_aligned.index)
    print(f"Annualization factor inferred: {ann_factor}")

    # ---------- Analysis 1: Sign-based ----------
    sign_based_analysis(returns_aligned, indicators_aligned, ann_factor)

    # ---------- Analysis 2: Systematic regime modeling ----------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(indicators_aligned.values)

    regime_labels = fit_regime_models(X_scaled, indicators_aligned.index)

    # ---------- Optional: Changepoint detection ----------
    cpd_labels = fit_changepoint_models(X_scaled, indicators_aligned.index, n_bkps=6)
    regime_labels.update(cpd_labels)

    regimes_df = per_regime_factor_stats(returns_aligned, ann_factor, regime_labels, indicators_aligned.index)

    # ---------- Dummies ----------
    _ = make_dummies(regimes_df, indicators_aligned)

    # ---------- Example “highlight timepoints” figure on one factor ----------
    try:
        # Prefer kmeans_ind if present; else take first model
        example_model = "kmeans_ind" if "kmeans_ind" in regimes_df.columns else regimes_df.columns[0]
        example_factor = returns_aligned.columns[0]
        cumret = (returns_aligned[example_factor]).cumsum().pipe(np.exp) - 1.0
        plot_series_with_regime_bands(
            returns_aligned.index, cumret, regimes_df[example_model].values,
            title=f"{example_factor} cumulative return — colored by {example_model}",
            fname=f"{example_factor}_{example_model}_bands"
        )
    except Exception as e:
        print(f"Skipped banded series example due to: {e}")

    # ---------- README ----------
    with open(os.path.join(OUTPUT_DIR, "README_outputs.txt"), "w") as f:
        f.write(
            "This folder contains outputs for regime analysis.\n\n"
            "Base prepared data:\n"
            "- returns_computed.csv: log returns aligned with indicators\n"
            "- indicators_shifted_by2d.csv: indicators shifted +2 days\n\n"
            "Sign-based outputs per indicator:\n"
            "- <ind>_mean_by_sign.csv / _vol_by_sign.csv / _sharpe_by_sign.csv\n"
            "- <ind>_*_heatmap.png\n\n"
            "Model-based regimes:\n"
            "- regimes_by_model.csv\n"
            "- exhibit4_<model>.png (timeline)\n"
            "- <model>_annualized_mean_by_regime.csv / _vol_ / _sharpe_\n"
            "- <model>_*_heatmap.png\n\n"
            "Changepoint detection (if ruptures installed):\n"
            "- exhibit4_cpd_*.png timelines and segment labels included in regimes_by_model.csv\n\n"
            "Dummies:\n"
            "- regime_and_sign_dummies.csv\n\n"
            "Extras:\n"
            "- <Factor>_<model>_bands.png (series with regime bands; gap-free via midpoint method)\n"
        )

    print(f"Done. Outputs saved under: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()