from django.db.models import Model

from webapp.models import Person


class Graph:
    """
    For use with antv/G6; see https://g6.antv.vision/en
    """
    padding = 50

    def __init__(self):
        self.added_people = set()
        self.nodes = set()
        self.edges = set()

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

        def __hash__(self):
            return hash(self.id)

        def __str__(self):
            return str(vars(self))

        def __repr__(self):
            return str(vars(self))

    class Edge:
        def __init__(self, source_id, target_id, label=None, **kwargs):
            self.source = source_id
            self.target = target_id
            self.label = label
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

        def __eq__(self, other):
            return self.source == other.source and self.target == other.target

        def __hash__(self):
            return hash((self.source, self.target))

        def __str__(self):
            return str(vars(self))

        def __repr__(self):
            return str(vars(self))

    @staticmethod
    def gen_id(model_object):
        return f'{type(model_object).__name__}_{model_object.pk}'

    def get_node(self, arg):
        if isinstance(arg, Model):
            return next(node for node in self.nodes if node.id == self.gen_id(arg))
        else:
            return next(node for node in self.nodes if node.id == arg)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)
        else:
            raise ValueError("Tried to add duplicate node")

    def remove_node(self, node):
        self.nodes.remove(node)
        self.edges = [edge for edge in self.edges if edge.source != node.id and edge.target != node.id]

    def add_person(self, person, x=0, y=0):
        self.add_node(self.Node(self.gen_id(person), x, y, str(person)))
        self.added_people.add(person)

    def remove_person(self, person):
        self.remove_node(self.get_node(person))
        self.added_people.remove(person)

    def add_edge(self, source_id, target_id):
        self.edges.add(self.Edge(source_id, target_id))

    def get_edge(self, source_id, target_id):
        return next(edge for edge in self.edges if edge.source == source_id and edge.target == target_id)

    def remove_edge(self, source_id, target_id):
        self.edges.remove(self.Edge(source_id, target_id))

    def add_partnership(self, partnership, x=0, y=0, padding_mult=1):
        self.add_node(self.Node(self.gen_id(partnership), x, y, size=1))
        partners = partnership.partners()
        if len(partners) == 2:
            self.add_person(partners[0], x - self.padding * padding_mult, y)
            self.add_person(partners[1], x + self.padding * padding_mult, y)
            self.add_edge(self.gen_id(partners[0]), self.gen_id(partnership))
            self.add_edge(self.gen_id(partners[1]), self.gen_id(partnership))
        # TODO: add logic for other numbers of partners

    def add_parents(self, person, x=None, y=None, depth=1):
        if depth > 0:
            # default x and y to coordinates of the node matching person
            person_node = self.get_node(person)
            x = x or person_node.x or 0
            y = y or person_node.y or 0

            # TODO: add support for multiple partnerships
            parents = person.parents()[0]
            self.add_partnership(parents, x, y - self.padding, padding_mult=depth)
            self.add_edge(self.gen_id(parents), self.gen_id(person))

            # TODO: add support for >2 partners
            for parent in parents.partners()[:2]:
                if parent.parents():
                    self.add_parents(parent, depth=depth - 1)

    def get_gen_size(self, partnership, max_depth=1):
        """
        Calculates the maximum number of children per family in the max_depth generation for padding the rows above it
        properly
        :param partnership: Partnership to obtain the children from
        :param max_depth: number of generations to descend. 1 only obtains the first generation children of partnership
        :return: the maximum number of children per family in the max_depth generation
        """
        if max_depth == 0:
            return 1

        next_gen_size = 0
        children = partnership.children.all()
        for child in children:
            if child.partnerships.exists():
                next_gen_size = max(next_gen_size,
                                     self.get_gen_size(next(iter(child.partnerships.all())), max_depth - 1))
        return len(children) * (next_gen_size or 1)

    def add_children(self, partnership, x=None, y=None, depth=1):
        if depth > 0:
            # default x and y to coordinates of the node matching partnership
            x = x or self.get_node(partnership).x or 0
            y = y or self.get_node(partnership).y or 0

            children = list(partnership.children.all())
            n = len(children)

            # pad row to allow for children, allowing for there being more nodes in the parent row than any child group
            gen_size = max(3 if any(child for child in children if child.partnerships.exists()) else 1,
                           self.get_gen_size(partnership, depth))

            extra = 0
            for i in range(n):
                child: Person = children[i]
                """
                pos = start of gen + distance between nodes 
                x is x of parents, so -n/2 to center all children
                +1/2 since the child nodes are centered in the space allotted for them
                scale by padding to spread them out
                scale by gen_size to ensure all families have equal space
                """
                xi = gen_size * self.padding * ((1 - n) / 2 + i) + x
                if child.partnerships.exists():
                    child_partnership = next(iter(child.partnerships.all()))
                    self.add_partnership(child_partnership, xi, y + self.padding)
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
