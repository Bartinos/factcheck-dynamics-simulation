import mesa
import networkx as nx


class NetworkAgent(mesa.Agent):
    def __init__(self, model, believes=False):
        super().__init__(model)
        self.believes = believes


class NetworkModel(mesa.Model):
    def __init__(
        self, graph=None, *, initial_believers=(), p0=0.02, peer_influence=0.20, rng=None
    ):
        super().__init__(rng=rng)
        self.graph = nx.Graph() if graph is None else graph.copy()
        self.p0 = p0
        self.peer_influence = peer_influence

        initial_believers = set(initial_believers)
        self.agents_by_node = {
            node: NetworkAgent(self, believes=node in initial_believers)
            for node in self.graph
        }

    def believing_neighbor_fraction(self, node):
        neighbors = list(self.graph.neighbors(node))
        if not neighbors:
            return 0.0
        believing_neighbors = sum(
            self.agents_by_node[neighbor].believes for neighbor in neighbors
        )
        return believing_neighbors / len(neighbors)

    def adoption_probability(self, node):
        neighbor_fraction = self.believing_neighbor_fraction(node)
        return min(1.0, self.p0 + self.peer_influence * neighbor_fraction)

    def step(self):
        # Decide who adopts using the current beliefs before changing any of them.
        adopters = [
            agent
            for node, agent in self.agents_by_node.items()
            if not agent.believes and self.random.random() < self.adoption_probability(node)
        ]
        for agent in adopters:
            agent.believes = True
