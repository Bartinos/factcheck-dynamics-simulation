from random import Random

import networkx as nx
import solara
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from mesa.visualization import SolaraViz
from mesa.visualization.utils import update_counter

from model import NetworkModel
from plots import plot_prevalence


SEED = 42
AGENT_COUNT = 200
TARGET_AVERAGE_DEGREE = 6
DEFAULT_FACT_CHECK_STEP = 5
DEFAULT_PEER_INFLUENCE = 0.20
GRAPH = nx.fast_gnp_random_graph(
    AGENT_COUNT, TARGET_AVERAGE_DEGREE / (AGENT_COUNT - 1), seed=SEED
)
INITIAL_BELIEVERS = tuple(Random(SEED).sample(list(GRAPH), AGENT_COUNT // 10))
ISOLATED_NODES = tuple(nx.isolates(GRAPH))
CONNECTED_NODES = [node for node, degree in GRAPH.degree if degree > 0]
POSITIONS = nx.kamada_kawai_layout(GRAPH.subgraph(CONNECTED_NODES))
POSITIONS.update(
    {
        node: ((index - (len(ISOLATED_NODES) - 1) / 2) * 0.12, -1.15)
        for index, node in enumerate(ISOLATED_NODES)
    }
)
REJECTS_COLOR = "#2563a8"
BELIEVES_COLOR = "#c43c3c"
BELIEF_LEGEND = [
    Line2D([], [], color=REJECTS_COLOR, marker="o", linestyle="none", label="Rejects the claim"),
    Line2D([], [], color=BELIEVES_COLOR, marker="o", linestyle="none", label="Believes the claim"),
]

@solara.component
def NetworkView(model):
    revision = update_counter.get()
    figure = Figure(figsize=(8, 7), layout="constrained")
    axes = figure.subplots()
    nx.draw_networkx_edges(
        model.graph, POSITIONS, ax=axes, edge_color="#64748b", width=0.55, alpha=0.25
    )
    nx.draw_networkx_nodes(
        model.graph,
        POSITIONS,
        nodelist=list(model.agents_by_node),
        node_color=[
            BELIEVES_COLOR if agent.believes else REJECTS_COLOR
            for agent in model.agents_by_node.values()
        ],
        node_size=32,
        edgecolors="white",
        linewidths=0.45,
        ax=axes,
    )
    if ISOLATED_NODES:
        label = "Isolated node" if len(ISOLATED_NODES) == 1 else "Isolated nodes"
        axes.annotate(
            label,
            (0, -1.15),
            xytext=(0, -8),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=9,
        )
    axes.margins(0.08)
    axes.set_axis_off()
    axes.set_aspect("equal")
    figure.legend(
        handles=BELIEF_LEGEND,
        loc="outside upper center",
        ncols=2,
        frameon=False,
    )
    solara.FigureMatplotlib(figure, dependencies=[model, revision])


@solara.component
def PrevalenceView(model):
    revision = update_counter.get()
    solara.FigureMatplotlib(plot_prevalence(model), dependencies=[model, revision])


model_params = {
    "graph": GRAPH,
    "initial_believers": INITIAL_BELIEVERS,
    "rng": SEED,
    "fact_check_step": {
        "type": "Select",
        "label": "Fact-check step",
        "value": DEFAULT_FACT_CHECK_STEP,
        "values": [5, 20],
    },
    "peer_influence": {
        "type": "Select",
        "label": "Peer influence",
        "value": DEFAULT_PEER_INFLUENCE,
        "values": [0.20, 0.60],
    },
}


@solara.component
def Page():
    initial_model = solara.use_memo(
        lambda: NetworkModel(
            GRAPH,
            initial_believers=INITIAL_BELIEVERS,
            fact_check_step=DEFAULT_FACT_CHECK_STEP,
            peer_influence=DEFAULT_PEER_INFLUENCE,
            rng=SEED,
        ),
        [],
    )
    model = solara.use_reactive(initial_model)
    with solara.Column():
        SolaraViz(
            model,
            model_params=model_params,
            name="Fact-checking dynamics",
            play_interval=350,
        )
        solara.ColumnsResponsive(
            default=12,
            large=[8, 4],
            children=[NetworkView(model.value), PrevalenceView(model.value)],
        )
