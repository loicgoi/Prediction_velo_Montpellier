from datetime import datetime
import numpy as np
from matplotlib.axes import Axes


def apply_dashboard_style(ax: Axes):
    """Applies a basic style to the dashboard charts."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle=":", alpha=0.5, axis="y")


def plot_history_30d(ax: Axes, data: list, prediction_today: int):
    """Displays the history for the last 30 days and the forecast for today."""
    if not data:
        data = [0] * 30

    days = np.arange(len(data))
    ax.plot(days, data, color="#94a3b8", label="Réel (30j)")
    ax.fill_between(days, data, color="#94a3b8", alpha=0.1)
    ax.plot(
        len(data),
        prediction_today,
        marker="o",
        color="#2563eb",
        markersize=8,
        label="Prév. J",
    )
    ax.set_title("Tendance 30 jours + Prévision", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    apply_dashboard_style(ax)


def plot_accuracy_7d(ax: Axes, real: list, pred: list):
    """Displays a bar chart comparing predictions and actual values over 7 days."""
    if not real:
        real = [0] * 7
    if not pred:
        pred = [0] * 7

    days = ["J-7", "J-6", "J-5", "J-4", "J-3", "J-2", "Hier"]
    x = np.arange(len(days))
    width = 0.35
    ax.bar(x - width / 2, pred, width, label="Prédit", color="#cbd5e1")
    ax.bar(x + width / 2, real, width, label="Réel", color="#3b82f6")
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=7)
    ax.set_title("Fiabilité (7j)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    apply_dashboard_style(ax)


def plot_weekly_averages(ax: Axes, averages: list):
    """Displays the average number of visits for each day of the week."""
    if not averages or len(averages) < 7:
        averages = [0] * 7

    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    colors = ["#cbd5e1"] * 7
    colors[datetime.now().weekday()] = "#2563eb"
    bars = ax.bar(days, averages, color=colors)
    ax.set_title("Profil Hebdo", fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", labelsize=8)
    ax.yaxis.set_ticks([])  # Remove the Y axis for clarity
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom",
            fontsize=7,
        )
    apply_dashboard_style(ax)


def plot_weekly_totals(ax: Axes, totals: list):
    """Displays the change in traffic volume over the last 12 weeks."""
    if not totals:
        totals = [0] * 12

    weeks = np.arange(len(totals))
    ax.plot(weeks, totals, marker="o", linestyle="-", color="#2563eb", linewidth=1.5)
    ax.set_title("Volume (12 sem.)", fontsize=10, fontweight="bold")
    ax.set_xlabel("Semaines", fontsize=8)
    apply_dashboard_style(ax)
