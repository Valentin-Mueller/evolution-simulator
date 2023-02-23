class Organism():
    pass


class Pair():

    def __init__(self, organism_a: Organism, organism_b: Organism) -> None:
        self.parent_a = organism_a
        self.parent_b = organism_b

    def produce_offspring(self) -> Organism:
        pass
