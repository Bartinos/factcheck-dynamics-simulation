import mesa
import networkx as nx


class NetworkAgent(mesa.Agent):
    def __init__(self, model, believes=False):
        super().__init__(model)
        self.believes = believes


class NetworkModel(mesa.Model):
    def __init__(
        self,
        graph=None,
        *,
        initial_believers=(),
        p0=0.02,
        peer_influence=0.20,
        fact_check_step=None,
        correction_probability=0.70,
        rng=None,
    ):
        super().__init__(rng=rng)
        self.graph = nx.Graph() if graph is None else graph.copy()
        self.p0 = p0
        self.peer_influence = peer_influence
        self.fact_check_step = fact_check_step
        self.correction_probability = correction_probability

        initial_believers = set(initial_believers)
        self.agents_by_node = {
            node: NetworkAgent(self, believes=node in initial_believers)
            for node in self.graph
        }
        self.prevalence_history = [self.prevalence()]

    def prevalence(self):
        agents = self.agents_by_node.values()
        if not agents:
            return None
        return sum(agent.believes for agent in agents) / len(agents)

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
        # Decide both updates from the starting beliefs before applying any changes.
        adopters = [
            agent
            for node, agent in self.agents_by_node.items()
            if not agent.believes and self.random.random() < self.adoption_probability(node)
        ]
        corrected = []
        if self.time == self.fact_check_step:
            corrected = [
                agent
                for agent in self.agents_by_node.values()
                if agent.believes and self.random.random() < self.correction_probability
            ]

        for agent in adopters:
            agent.believes = True
        for agent in corrected:
            agent.believes = False

        self.prevalence_history.append(self.prevalence())
