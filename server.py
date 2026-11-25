from random import Random

import networkx as nx
import solara
from matplotlib.figure import Figure
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
POSITIONS = nx.spring_layout(GRAPH, seed=SEED)


# The live Matplotlib component follows the course's Basic Network notebook and
# CustomSpaceVisualization in the symbiotic-relationships-simulation server.py.
@solara.component
def NetworkView(model):
    revision = update_counter.get()
    figure = Figure(figsize=(6, 5), layout="constrained")
    axes = figure.subplots()
    nx.draw_networkx_edges(model.graph, POSITIONS, ax=axes, edge_color="0.72", alpha=0.5)
    believers = [node for node, agent in model.agents_by_node.items() if agent.believes]
    rejecters = [node for node, agent in model.agents_by_node.items() if not agent.believes]
    nx.draw_networkx_nodes(
        model.graph,
        POSITIONS,
        nodelist=rejecters,
        node_color="tab:blue",
        node_size=28,
        label="Rejects the claim",
        ax=axes,
    )
    nx.draw_networkx_nodes(
        model.graph,
        POSITIONS,
        nodelist=believers,
        node_color="tab:red",
        node_size=28,
        label="Believes the claim",
        ax=axes,
    )
    axes.set_axis_off()
    axes.set_aspect("equal")
    axes.legend(loc="upper right")
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
    model = solara.use_memo(
        lambda: NetworkModel(
            GRAPH,
            initial_believers=INITIAL_BELIEVERS,
            fact_check_step=DEFAULT_FACT_CHECK_STEP,
            peer_influence=DEFAULT_PEER_INFLUENCE,
            rng=SEED,
        ),
        [],
    )
    return SolaraViz(
        model,
        components=[(NetworkView, 0), (PrevalenceView, 0)],
        model_params=model_params,
        name="Fact-checking dynamics",
        play_interval=350,
    )
