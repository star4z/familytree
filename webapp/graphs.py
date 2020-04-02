from webapp.models import Person


class Graph:
    """
    For use with antv/G6; see https://g6.antv.vision/en
    """
    padding = 50

    def __init__(self):
        self.added_people = []
        self.nodes = []
        self.edges = []

    class Node:
        def __init__(self, id_, x=None, y=None, label=None, **kwargs):
            self.id = id_
            self.x = x
            self.y = y
            self.label = label
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

        def __eq__(self, other):
            return self.id == other.id

    class Edge:
        def __init__(self, source, target, label=None, **kwargs):
            self.source = source
            self.target = target
            self.label = label
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

    @staticmethod
    def gen_id(model_object):
        return f'{type(model_object).__name__}_{model_object.pk}'

    def get_node(self, model_object):
        return next(node for node in self.nodes if node.id == self.gen_id(model_object))

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
        else:
            raise ValueError("Tried to add duplicate node")

    def add_person(self, person, x, y):
        self.add_node(self.Node(self.gen_id(person), x, y, str(person)))
        self.added_people.append(person)

    def add_edge(self, source, target):
        self.edges.append(self.Edge(source, target))

    def add_partnership(self, partnership, x, y):
        self.add_node(self.Node(self.gen_id(partnership), x, y, size=1))
        partners = partnership.partners()
        if len(partners) == 2:
            self.add_person(partners[0], x - self.padding, y)
            self.add_person(partners[1], x + self.padding, y)
            self.add_edge(self.gen_id(partners[0]), self.gen_id(partnership))
            self.add_edge(self.gen_id(partners[1]), self.gen_id(partnership))
        # TODO: add logic for other numbers of partners

    def add_parents(self, person, x=None, y=None, depth=1):
        if depth > 0:
            # default x and y to coordinates of the node matching person
            person_node = self.get_node(person)
            x = x or person_node.x
            y = y or person_node.y

            # TODO: add support for multiple partnerships
            parents = person.parents()[0]
            self.add_partnership(parents, x, y - self.padding)
            self.add_edge(self.gen_id(parents), self.gen_id(person))

            # TODO: add support for >2 partners
            for parent in parents.partners()[:2]:
                if parent.parents():
                    self.add_parents(parent, depth=depth - 1)

    def add_children(self, partnership, x=None, y=None, depth=1):
        if depth > 0:
            # default x and y to coordinates of the node matching partnership
            x = x or self.get_node(partnership).x
            y = y or self.get_node(partnership).y

            children = list(partnership.children.all())
            n = len(children)
            extra = 0
            for i in range(n):
                child: Person = children[i]
                xi = -self.padding / 2 * (n - 1) + self.padding * i + x + extra
                if child.partnerships.exists():
                    px = xi + self.padding
                    child_partnership = next(iter(child.partnerships.all()))
                    self.add_partnership(child_partnership, px, y + self.padding)
                    extra += self.padding * 2
                    self.add_children(child_partnership, depth=depth - 1)
                else:
                    self.add_person(child, xi, y + self.padding)
                self.add_edge(self.gen_id(partnership), self.gen_id(child))

    def normalize(self, extra_padding=0):
        min_x = min(node.x for node in self.nodes)
        min_y = min(node.y for node in self.nodes)
        for node in self.nodes:
            node.x += extra_padding - min_x
            node.y += extra_padding - min_y
        return self

    def to_dict(self):
        return {
            'nodes': [vars(node) for node in self.nodes],
            'edges': [vars(edge) for edge in self.edges]
        }
