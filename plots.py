from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, PercentFormatter

from model import NetworkModel


def plot_prevalence(model: NetworkModel, *, threshold: float = 0.05) -> Figure:
    """Plot one run's belief prevalence, including initialization at step zero."""
    history = model.prevalence_history
    figure = Figure(figsize=(6, 4), layout="constrained")
    axes = figure.subplots()
    axes.plot(range(len(history)), history, marker="o", markersize=3, label="Prevalence")
    axes.axhline(threshold, color="0.45", linestyle=":", label=f"{threshold * 100:g}% threshold")

    fact_check_step = model.fact_check_step
    if fact_check_step is not None and 1 <= fact_check_step < len(history):
        axes.axvline(fact_check_step, color="tab:orange", linestyle="--", label="Fact-check")

    axes.set(xlabel="Time step", ylabel="Agents who believe the claim", ylim=(0, 1))
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    axes.legend()
    return figure
