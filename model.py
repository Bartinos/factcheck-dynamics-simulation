import mesa


class NetworkAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)


class NetworkModel(mesa.Model):
    def __init__(self, *, rng=None):
        super().__init__(rng=rng)

    def step(self):
        pass
