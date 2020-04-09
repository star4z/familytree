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

        def is_overlapping(self, other):
            # TODO: replace with more robust function
            return self.x == other.x and self.y == other.y

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

    def add_children(self, partnership, x=None, y=None, depth=1):
        if depth > 0:
            # default x and y to coordinates of the node matching partnership
            x = x or self.get_node(partnership).x or 0
            y = y or self.get_node(partnership).y or 0

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

    def get_parents(self, person):
        person_node = self.get_node(person)
        parent_partnerships = {edge.source for edge in self.edges if edge.target == person_node.id}
        parents = {self.get_node(edge.source) for edge in self.edges if edge.target in parent_partnerships}
        return parents

    def apply_to_parents(self, person, function):
        for parent in self.get_parents(person):
            function(parent)

    def get_children(self, partnership):
        person_node = self.get_node(partnership)
        children = {self.get_node(edge.target) for edge in self.edges if edge.source == person_node.id}
        return children

    def apply_to_children(self, partnership, function):
        for child in self.get_children(partnership):
            function(child)

    def normalize(self, extra_padding=0):
        min_x = min(node.x for node in self.nodes)
        min_y = min(node.y for node in self.nodes)
        for node in self.nodes:
            node.x += extra_padding - min_x
            node.y += extra_padding - min_y
            #
            # for other_node in self.nodes:
            #     if node.is_overlapping(other_node):
            #         # make node and other_node not overlap
            #         edges = [edge for edge in self.edges if edge.source == node.id]
            #         if any(target_node := self.get_node(edge.target) for edge in edges if node.x < target_node.x and node.y == target_node.y):
            #             # node is right node
            #             node.x += self.padding
            #             self.apply_to_parents()
            #         else:
            #             # node is left node
            #             pass
        return self

    def to_dict(self):
        return {
            'nodes': [vars(node) for node in self.nodes],
            'edges': [vars(edge) for edge in self.edges]
        }
