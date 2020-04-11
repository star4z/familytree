import datetime

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase

from webapp.graphs import Graph
from webapp.models import LegalName, Partnership, Person, PersonPartnership, Tree


class ModelTestCase(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(title='test tree')

    def create_person(self, first_name, gender, partnership_ids=None, **kwargs):
        genders = {'M': 'Male', 'F': 'Female'}
        legal_name = LegalName.objects.create(first_name=first_name)
        legal_name.save()
        p = Person.objects.create(tree=self.tree, legal_name=legal_name, gender=genders[gender], **kwargs)
        p.save()
        if partnership_ids:
            for pid in partnership_ids:
                partnership = self.get_partnership(pid)
                person_partnership = PersonPartnership.objects.create(person=p, partnership=partnership)
                person_partnership.save()
        return p

    def get_partnership(self, pid):
        partnership, created = Partnership.objects.get_or_create(id=pid, defaults={'tree': self.tree})
        partnership.save()
        return partnership


class PersonTestCase(ModelTestCase):
    def setUp(self):
        super().setUp()

        self.abe = self.create_person('Abe', 'M', [1])
        self.beth = self.create_person('Beth', 'F', [1])
        self.dave = self.create_person('Dave', 'M', [2])
        self.jeanine = self.create_person('Jeanine', 'F', [2])
        birth_date = datetime.date(1900, 1, 1)
        death_date = datetime.date(1980, 1, 1)
        self.philip = self.create_person('Philip', 'M', [3], birth_date=birth_date, death_date=death_date, living=False)
        self.megumi = self.create_person('Megumi', 'F', [3], birth_date=birth_date, living=False)
        self.akito = self.create_person('Akito', 'M', [4])
        self.nala = self.create_person('Nala', 'F', [4])
        self.colin = self.create_person('Colin', 'M')
        self.akira = self.create_person('Akira', 'F')
        self.elizabeth = self.create_person('Elizabeth', 'F', [5])
        self.kassandra = self.create_person('Kassandra', 'F', [5])
        self.john = self.create_person('John', 'M')
        self.violet = self.create_person('Violet', 'F', living=True)
        birth_date = datetime.date(2000, 1, 1)
        self.pablo = self.create_person('Pablo', 'M', birth_date=birth_date, living=True)

        self.get_partnership(1).children.add(self.dave)  # Dave is Abe and Beth's child
        self.get_partnership(2).children.add(self.philip)  # Philip is Dave and Jeanine's child
        self.get_partnership(3).children.add(self.akito)  # Akito is Philip and Megumi's child
        self.get_partnership(4).children.add(self.colin)  # Colin is Akito and Nala's child
        self.get_partnership(4).children.add(self.akira)  # Akira is Akito and Nala's child
        self.get_partnership(3).children.add(self.elizabeth)  # Elizabeth is Philip and Megumi's child
        self.get_partnership(5).children.add(self.john)  # John is Elizabeth and Kassandra's child
        self.get_partnership(5).children.add(self.violet)  # Violet is Elizabeth and Kassandra's child

        self.gen2 = [self.get_partnership(1)]
        self.gen1 = [self.get_partnership(2)]
        self.gen0 = [self.philip]
        self.genN1 = [self.akito, self.elizabeth]
        self.genN2 = [self.colin, self.akira, self.john, self.violet]

    def test_get_parents(self):
        parents = list(self.philip.parents())
        self.assertListEqual(self.gen1, parents)

    def test_get_gen_two(self):
        generation = list(self.philip.get_generation(2))
        self.assertListEqual(self.gen2, generation)

    def test_get_gen_one(self):
        generation = list(self.philip.get_generation(1))
        self.assertListEqual(self.gen1, generation)

    def test_get_gen_zero(self):
        generation = [self.philip.get_generation(0)]
        self.assertListEqual(self.gen0, generation)

    def test_get_gen_neg_one(self):
        generation = list(self.philip.get_generation(-1))
        self.assertListEqual(self.genN1, generation)

    def test_get_gen_neg_two(self):
        generation = list(self.philip.get_generation(-2))
        self.assertListEqual(self.genN2, generation)

    def test_get_siblings(self):
        expected = [self.akira]
        actual = list(self.colin.siblings())
        self.assertListEqual(expected, actual)

    def test_get_siblings_empty_list(self):
        expected = []
        actual = list(self.philip.siblings())
        self.assertListEqual(expected, actual)

    def test_age_dead_with_death_date(self):
        expected = relativedelta(years=80)
        actual = self.philip.age()
        self.assertEqual(expected, actual)

    def test_age_dead_without_death_date(self):
        with self.assertRaises(Person.IllegalAgeError):
            self.megumi.age()

    def test_age_living_with_birth_date(self):
        expected = relativedelta(datetime.date.today(), self.pablo.birth_date)
        actual = self.pablo.age()
        self.assertEqual(expected, actual)

    def test_age_without_birth_date(self):
        with self.assertRaises(Person.IllegalAgeError):
            self.violet.age()

    def test_illegal_age_range_raises_error(self):
        with self.assertRaises(ValidationError):
            birth_date = datetime.date(2000, 1, 2)
            death_date = datetime.date(2000, 1, 1)
            instance = self.create_person('default', 'M', birth_date=birth_date, death_date=death_date)
            instance.clean()


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
