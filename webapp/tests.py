from commons.tests import ModelTestCase
from webapp.graphs import Graph


class TestGraph(ModelTestCase):
    def setUp(self):
        super().setUp()
        self.graph = Graph()
        self.opal = self.create_person('Opal', 'F', [1])
        self.bruno = self.create_person('Bruno', 'M', [1])
        self.talia = self.create_person('Talia', 'F')
        self.darrel = self.create_person('Darrel', 'M')
        self.jacob = self.create_person('Jacob', 'M')
        p1_children = self.get_partnership(1).children
        p1_children.add(self.talia)
        p1_children.add(self.darrel)
        p1_children.add(self.jacob)

        self.margaret = self.create_person('Margaret', 'F', [2])
        self.chris = self.create_person('Chris', 'M', [2])
        self.get_partnership(2).children.add(self.opal)

    def test_gen_id(self):
        expected = f'Person_{self.opal.pk}'
        actual = self.graph.gen_id(self.opal)
        self.assertEqual(expected, actual)

    def test_add_node(self):
        node = Graph.Node('test_id')
        self.graph.add_node(node)
        self.assertSetEqual({node}, self.graph.nodes)

    def test_get_node_by_id(self):
        node = Graph.Node('test_id')
        self.graph.add_node(node)
        self.assertEqual(node, self.graph.get_node('test_id'))

    def test_remove_node(self):
        node = Graph.Node('test_id')
        self.graph.add_node(node)
        self.graph.remove_node(node)
        self.assertSetEqual(set(), self.graph.nodes)

    def test_add_person(self):
        self.graph.add_person(self.opal, 100, 100)
        expected_nodes = {Graph.Node(self.graph.gen_id(self.opal), 100, 100, 'Opal')}
        self.assertSetEqual(expected_nodes, self.graph.nodes)
        expected_added_people = {self.opal}
        self.assertSetEqual(expected_added_people, self.graph.added_people)

    def test_get_node_by_model(self):
        self.graph.add_person(self.opal)
        self.assertEqual(self.graph.Node(self.graph.gen_id(self.opal)), self.graph.get_node(self.opal))

    def test_remove_person(self):
        self.graph.add_person(self.opal)
        self.graph.remove_person(self.opal)
        expected = set()
        self.assertSetEqual(expected, self.graph.nodes)

    def test_add_edge(self):
        node1 = Graph.Node('id1')
        node2 = Graph.Node('id2')
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_edge(node1.id, node2.id)

    def test_add_partnership(self):
        self.graph.add_partnership(self.get_partnership(1), 200, 200)
        opal_id = self.graph.gen_id(self.opal)
        bruno_id = self.graph.gen_id(self.bruno)
        partnership_id = self.graph.gen_id(self.get_partnership(1))
        expected_nodes = {self.graph.Node(opal_id), self.graph.Node(bruno_id), self.graph.Node(partnership_id)}
        self.assertSetEqual(expected_nodes, self.graph.nodes)
        expected_edges = {self.graph.Edge(opal_id, partnership_id), self.graph.Edge(bruno_id, partnership_id)}
        self.assertSetEqual(expected_edges, self.graph.edges)
        expected_added_people = {self.opal, self.bruno}
        self.assertSetEqual(expected_added_people, self.graph.added_people)

    def test_add_parents(self):
        self.graph.add_person(self.opal)
        self.graph.add_parents(self.opal)
        opal_id = self.graph.gen_id(self.opal)
        margaret_id = self.graph.gen_id(self.margaret)
        chris_id = self.graph.gen_id(self.chris)
        partnership_id = self.graph.gen_id(self.get_partnership(2))
        expected_nodes = {
            self.graph.Node(opal_id),
            self.graph.Node(margaret_id),
            self.graph.Node(chris_id),
            self.graph.Node(partnership_id)
        }
        self.assertSetEqual(expected_nodes, self.graph.nodes)
        expected_edges = {
            self.graph.Edge(margaret_id, partnership_id),
            self.graph.Edge(chris_id, partnership_id),
            self.graph.Edge(partnership_id, opal_id)
        }
        self.assertSetEqual(expected_edges, self.graph.edges)
        expected_added_people = {self.opal, self.margaret, self.chris}
        self.assertSetEqual(expected_added_people, self.graph.added_people)

    def test_get_gen_size(self):
        self.assertEqual(3, self.graph.get_gen_size(self.get_partnership(2), 2))
        self.assertEqual(1, self.graph.get_gen_size(self.get_partnership(2), 1))
        self.assertEqual(3, self.graph.get_gen_size(self.get_partnership(1), 1))

    def test_get_family_size(self):
        self.assertEqual(3, self.graph.get_family_size(self.get_partnership(2), 2))
        self.assertEqual(3, self.graph.get_family_size(self.get_partnership(2), 1))
        self.assertEqual(3, self.graph.get_family_size(self.get_partnership(1), 1))

        self.create_person('Peter', 'M', [3])
        sasha = self.create_person('Sasha', 'F', [3])
        self.get_partnership(2).children.add(sasha)

        brian = self.create_person('Brian', 'M')
        self.get_partnership(2).children.add(brian)

        self.assertEqual(7, self.graph.get_family_size(self.get_partnership(2), 1))
        self.assertEqual(7, self.graph.get_family_size(self.get_partnership(2), 2))
        self.assertEqual(3, self.graph.get_family_size(self.get_partnership(1), 1))
