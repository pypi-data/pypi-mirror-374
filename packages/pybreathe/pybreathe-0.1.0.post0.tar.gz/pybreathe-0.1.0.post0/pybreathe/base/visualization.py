#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions that handle plots.

Created on Wed Apr  9 08:30:59 2025
@author: CoustilletT
"""


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from scipy.integrate import trapezoid
from scipy.signal import find_peaks
import seaborn as sns

from . import featureextraction as features
from .utils import scientific_round


def plot_signal(
    x, y, show_segments, show_auc, highlight_time, highlight_auc, output_path
):
    """To plot y versus x.

    Args:
    ----
        x (array): the values for the x-axis.
        y (array): the values for the y-axis.
        show_segments (bool): to distinguish between the positive and negative
                              parts of the curve.
        show_auc (bool): to distinguish between the positive and negative
                         areas of the curve.
        highlight_time (tuple): to highlight breathing cycles with a specific time.
        highlight_auc (tuple): to highlight breathing cycles with a specific area.
        output_path (str): to choose where to save the figure, if applicable.

    Returns:
    -------
        None. Plot the figure.

    """
    positive_segments = features.get_segments(x, y)[0]
    negative_segments = features.get_segments(x, y)[1]

    positive_auc = features.get_auc_value(
        segments=positive_segments,
        return_mean=False,
        verbose=False,
        n_digits=2,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
    )

    negative_auc = features.get_auc_value(
        segments=negative_segments,
        return_mean=False,
        verbose=False,
        n_digits=2,
        lower_threshold=-np.inf,
        upper_threshold=np.inf,
    )

    pos_normalized = positive_auc / np.max(positive_auc)
    neg_normalized = negative_auc / np.min(negative_auc)

    cmap_pos, cmap_neg = plt.cm.GnBu, plt.cm.RdPu
    cmap_pos_normalized = cmap_pos(
        np.linspace(np.min(pos_normalized), np.max(pos_normalized), len(positive_auc))
    )
    cmap_neg_normalized = cmap_neg(
        np.linspace(np.max(neg_normalized), np.min(neg_normalized), len(negative_auc))
    )
    global_cmap = mcolors.ListedColormap(
        np.concatenate([cmap_neg_normalized, cmap_pos_normalized])
    )

    bbox_style = {
        "facecolor": "whitesmoke",
        "boxstyle": "round,pad=0.3",
        "edgecolor": "k",
        "lw": 0.2
    }

    fig, ax = plt.subplots(figsize=(14, 2))

    if show_segments:
        for i, (x_pos, y_pos) in enumerate(positive_segments):
            pos_label = "Air flow rate > 0" if i == 1 else ""
            ax.plot(x_pos, y_pos, label=pos_label, c="tab:blue")
        for i, (x_neg, y_neg) in enumerate(negative_segments):
            neg_label = "Air flow rate < 0" if i == 1 else ""
            ax.plot(x_neg, y_neg, label=neg_label, c="tab:orange")
    else:
        ax.plot(x, y, label="air flow rate", c="tab:gray", lw=1)
        ax.axhline(y=0, c="grey", linestyle=":", lw=1)
        zeros = np.where(y == 0)[0]
        ax.scatter(x[zeros], y[zeros], zorder=2, c="gold", s=9, lw=0.4, edgecolor="k")

    if show_auc:
        for i, (xp, yp) in enumerate(positive_segments):
            color = cmap_pos(pos_normalized[i])
            ax.fill_between(xp, yp, color=color, alpha=1)

        for j, (xn, yn) in enumerate(negative_segments):
            color = cmap_neg(neg_normalized[j])
            ax.fill_between(xn, yn, color=color, alpha=1)

        sm = ScalarMappable(
            norm=mcolors.TwoSlopeNorm(
                vmin=np.min(negative_auc), vcenter=0, vmax=np.max(positive_auc)
            ),
            cmap=global_cmap,
        )
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation="vertical")
        cbar.set_label("Area under the curve", labelpad=15)

    if highlight_time:
        for s in (positive_segments, negative_segments):
            cmap = cmap_pos if s == positive_segments else cmap_neg
            normalized = pos_normalized if s == positive_segments else neg_normalized
            for t in highlight_time:
                for i, (xs, ys) in enumerate(s):
                    if scientific_round((xs[-1] - xs[0]), n_digits=3) == t:
                        color = cmap(normalized[i])
                        ax.fill_between(xs, ys, color=color, alpha=1)
                        max_y = max(ys) if max(ys) > 0 else min(ys)
                        ax.text(
                            x=(xs[0] + xs[-1]) / 2,
                            y=max_y,
                            s=f"t={t}",
                            fontsize=8,
                            backgroundcolor="whitesmoke",
                            bbox=bbox_style
                        )

    if highlight_auc:
        for s in (positive_segments, negative_segments):
            cmap = cmap_pos if s == positive_segments else cmap_neg
            normalized = pos_normalized if s == positive_segments else neg_normalized
            for a in highlight_auc:
                for i, (xs, ys) in enumerate(s):
                    if scientific_round(trapezoid(y=ys, x=xs), n_digits=3) == a:
                        color = cmap(normalized[i])
                        ax.fill_between(xs, ys, color=color, alpha=1)
                        max_y = max(ys) if max(ys) > 0 else min(ys)
                        ax.text(
                            x=(xs[0] + xs[-1]) / 2,
                            y=max_y,
                            s=f"auc={a}",
                            fontsize=8,
                            backgroundcolor="whitesmoke",
                            bbox=bbox_style
                        )

    ax.set_xlabel("time (s)", labelpad=10)
    ax.set_ylabel("Air flow rate", labelpad=10)
    ax.set_title(
        f"{len(positive_segments)} positive segments & {len(negative_segments)} negative segments detected",
        fontsize=9,
        c="k",
        backgroundcolor="whitesmoke",
        bbox={
            "facecolor": "whitesmoke",
            "boxstyle": "round,pad=0.3",
            "edgecolor": "silver",
            "lw": 0.2,
        },
    )
    ax.grid(alpha=0.8, linestyle=":", ms=0.1, zorder=1)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, 1.2))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")


def plot_peaks(x, y, which_peaks, distance, output_path):
    """
    Calibration of peaks detection
    = test of the distance that correctly detects all the peaks.

    Args:
    ----
        x (array): the values for the x-axis.
        y (array): the values for the y-axis.
        which_peaks (str): to consider either top or bottom peaks.
        distance (int): the minimum distance between two neighbouring peaks.
        output_path (str): to choose where to save the figure, if applicable.

    Returns:
    -------
        None. Plots a control figure.

    """
    top_peaks, _ = find_peaks(y, distance=distance)
    bottom_peaks, _ = find_peaks(-y, distance=distance)

    fig, ax = plt.subplots(figsize=(14, 2))

    ax.plot(x, y, c="tab:blue", label="your signal", zorder=1)

    match which_peaks:
        case "top":
            ax.scatter(
                x[top_peaks],
                y[top_peaks],
                s=10,
                marker="x",
                lw=2,
                c="red",
                label=f"{len(top_peaks)} detected peaks (distance = {distance})",
                zorder=2,
            )
        case "bottom":
            ax.scatter(
                x[bottom_peaks],
                y[bottom_peaks],
                s=10,
                marker="x",
                lw=2,
                c="red",
                label=f"{len(bottom_peaks)} detected peaks (distance = {distance})",
                zorder=2,
            )
        case _:
            raise ValueError(
                "Argument 'which_peaks' must be either 'top' or 'bottom'. "
                f"Not '{which_peaks}'."
            )

    min_s, max_s = min(y), max(y)
    s_amp = max_s - min_s
    min_b, max_b = min_s - 0.25 * s_amp, max_s + 0.25 * s_amp
    ax.set_ylim(min_b, max_b)
    ax.set_xlabel("time (s)", labelpad=10)
    ax.set_ylabel("Air flow rate", labelpad=10)
    ax.grid(alpha=0.8, linestyle=":", ms=0.5)
    ax.legend(prop={"size": 8}, loc="upper left", bbox_to_anchor=(0, 1.25))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")


def plot_features_distribution(*args, stat, output_path):
    """
    To get the distribution of each feature of the 'BreathingFlow' object.

    Args:
    ----
        *args (array): all the values of one of the signal features.
        stat (str): aggregate statistic to compute in each bin.
        output_path (str): to choose where to save the figure, if applicable.

    Returns:
    -------
        None. Plots the distribution.

    """
    x1, x2, x3, x4 = args
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))

    sns.histplot(data=x1, kde=True, stat=stat, ax=ax1)
    sns.histplot(data=x2, kde=True, stat=stat, ax=ax2)
    sns.histplot(data=x3, kde=True, stat=stat, ax=ax3)
    sns.histplot(data=x4, kde=True, stat=stat, ax=ax4)

    for ax in fig.axes:
        ax.grid(alpha=0.8, linestyle=":", ms=0.5)
        ax.lines[0].set_color("crimson")
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

    for ax, lab, x in zip(
        fig.axes,
        ("time (AUC > 0) (s)", "time (AUC < 0) (s)", "AUC > 0", "AUC < 0"),
        args,
    ):
        ax.set_xlabel(lab, labelpad=10)
        if lab.endswith("(s)"):
            lab = lab[:-3]

        match stat:
            case "probability":
                ax.set_ylabel(rf"$\mathbb{{P}}$ ({lab})", labelpad=10)
            case "count":
                ax.set_ylabel(rf"count ({lab})", labelpad=10)
            case "frequency":
                ax.set_ylabel(rf"frequency ({lab})", labelpad=10)
            case "percent":
                ax.set_ylabel(rf"percentage ({lab})", labelpad=10)
            case "density":
                ax.set_ylabel(rf"density ({lab})", labelpad=10)

        ax.set_title(f"Distribution of {lab} (n = {len(x)})", pad=10)

    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")


def plot_phase_portrait(x, y, time_delay, hz, color_scheme):
    """
    To plot the phase portrait of the time series y.

    Args:
    ----
        x (array): time axis of the time series.
        y (array): y axis of the time series.
        time_delay (float): parameter for phase portrait offset: y(x) vs. y(x+t).
        hz (int): the sampling rate of the time series.
        color_scheme (str): whether the color is defined from time or respiratory phases.

    Returns:
    -------
        None. Plots the phase portrait of the time series.

    """
    if color_scheme not in ("time", "phases"):
        raise ValueError(
            f"color_scheme should be either 'time' or 'phases'. Not {color_scheme}."
        )

    time_delay *= hz
    time_delay = int(time_delay)

    # 2D plot.
    y0 = y[:-time_delay]
    y_tau = y[time_delay:]

    # 3D plot.
    x_3d = y[:-3*time_delay:]
    y_3d = y[time_delay:-2*time_delay]
    z_3d = y[3*time_delay:]

    if color_scheme == "time":
        cmap = plt.cm.viridis(np.linspace(0, 1, len(y)))
    else:
        cmap = np.where(y > 0, "tab:blue", "tab:orange")

    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], width_ratios=[1, 1.5])
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1], projection="3d")

    # ax1.
    segments_1 = np.array([[[x[i], y[i]], [x[i+1], y[i+1]]] for i in range(len(x)-1)])
    lc1 = LineCollection(segments_1, colors=cmap)
    ax1.add_collection(lc1)
    legend_1 = Line2D([0], [0], color=cmap[0], label="air flow rate")
    ax1.legend(handles=[legend_1], fontsize=8, loc="upper left")
    ax1.autoscale()

    # ax2.
    segments_2 = np.array([[[y0[i], y_tau[i]], [y0[i+1], y_tau[i+1]]] for i in range(len(y0)-1)])
    lc2 = LineCollection(segments_2, colors=cmap)
    ax2.add_collection(lc2)
    legend_2 = Line2D([0], [0], color=cmap[0], label="phase portrait 2D")
    ax2.legend(handles=[legend_2], fontsize=8, loc="upper left")
    ax2.autoscale()

    segments_3d = np.array([[[x_3d[i], y_3d[i], z_3d[i]], [x_3d[i+1], y_3d[i+1], z_3d[i+1]]] for i in range(len(x_3d)-1)])
    lc3 = Line3DCollection(segments_3d, colors=cmap, linewidths=2)
    ax3.add_collection(lc3)
    legend_3 = Line2D([0], [0], color=cmap[0], label="phase portrait 3D")
    ax3.legend(handles=[legend_3], fontsize=8, loc="upper left")

    ax3.set_xlim(np.min(x_3d), np.max(x_3d))
    ax3.set_ylim(np.min(y_3d), np.max(y_3d))
    ax3.set_zlim(np.min(z_3d), np.max(z_3d))

    for ax in fig.get_axes():
        ax.grid(alpha=0.8, linestyle=":", ms=0.1, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax1.set_xlabel("time (s)", labelpad=10)
    ax1.set_ylabel("Air flow rate", labelpad=10)

    ax2.set_xlabel("y(t)", labelpad=10)
    ax2.set_ylabel(f"y(t + {time_delay / hz})", labelpad=10)

    ax3.set_xlabel("y(t)", labelpad=10)
    ax3.set_ylabel(f"y(t + {time_delay / hz})", labelpad=10)
    ax3.set_zlabel(f"y(t + {2*time_delay / hz})", labelpad=10)
