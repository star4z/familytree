class Graph:
    def __init__(self):
        self.added_people = []
        self.nodes = []
        self.edges = []

    class Node:
        def __init__(self, pk, x=None, y=None, label=None):
            self.id = pk
            self.x = x
            self.y = y
            self.label = label

    class Edge:
        def __init__(self, source, target, label=None):
            self.source = source
            self.target = target
            self.label = label

    @staticmethod
    def gen_id(model_object):
        return f'{type(model_object).__name__}_{model_object.pk}'

    def add_person(self, person, x, y):
        self.nodes.append(self.Node(self.gen_id(person), x, y, str(person)))

    def add_partnership(self, partnership, x, y):
        pass

    def to_json(self):
        return {
            'nodes': [vars(node) for node in self.nodes],
            'edges': [vars(edge) for edge in self.edges]
        }
