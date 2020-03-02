from django.test import TestCase
from webapp import models


class PersonTestCase(TestCase):
    def setUp(self):
        tree = models.Tree.objects.create(title='test tree')
        partnerships = [self.create_partnership(tree) for _ in range(5)]
        # persons = [
        self.abe = self.create_person(tree, 'Abe', 'M', partnerships[0])
        self.beth = self.create_person(tree, 'Beth', 'F', partnerships[0])
        self.dave = self.create_person(tree, 'Dave', 'M', partnerships[1])
        self.jeanine = self.create_person(tree, 'Jeanine', 'F', partnerships[1])
        self.philip = self.create_person(tree, 'Philip', 'M', partnerships[2])
        self.megumi = self.create_person(tree, 'Megumi', 'F', partnerships[2])
        self.akito = self.create_person(tree, 'Akito', 'M', partnerships[3])
        self.nala = self.create_person(tree, 'Nala', 'F', partnerships[3])
        self.colin = self.create_person(tree, 'Colin', 'M')
        self.akira = self.create_person(tree, 'Akira', 'F')
        self.elizabeth = self.create_person(tree, 'Elizabeth', 'F', partnerships[4])
        self.kassandra = self.create_person(tree, 'Kassandra', 'F', partnerships[4])
        self.john = self.create_person(tree, 'John', 'M')
        self.violet = self.create_person(tree, 'Violet', 'F')
        # ]

        partnerships[0].children.add(self.dave)  # Dave is Abe and Beth's child
        partnerships[1].children.add(self.philip)  # Philip is Dave and Jeanine's child
        partnerships[2].children.add(self.akito)  # Akito is Philip and Megumi's child
        partnerships[3].children.add(self.colin)  # Colin is Akito and Nala's child
        partnerships[3].children.add(self.akira)  # Akira is Akito and Nala's child
        partnerships[2].children.add(self.elizabeth)  # Elizabeth is Philip and Megumi's child
        partnerships[4].children.add(self.john)  # John is Elizabeth and Kassandra's child
        partnerships[4].children.add(self.violet)  # Violet is Elizabeth and Kassandra's child

        self.gen2 = [partnerships[0]]
        self.gen1 = [partnerships[1]]
        self.gen0 = [self.philip]
        self.genN1 = [self.akito, self.elizabeth]
        self.genN2 = [self.colin, self.akira, self.john, self.violet]

    @staticmethod
    def create_person(tree, first_name, gender, partnership=None):
        genders = {'M': 'Male', 'F': 'Female'}
        legal_name = models.LegalName.objects.create(first_name=first_name)
        legal_name.save()
        p = models.Person.objects.create(tree=tree, legal_name=legal_name, gender=genders[gender])
        p.save()
        if partnership:
            person_partnership = models.PersonPartnership.objects.create(person=p, partnership=partnership)
            person_partnership.save()
        return p

    @staticmethod
    def create_partnership(tree):
        partnership = models.Partnership.objects.create(tree=tree)
        partnership.save()
        return partnership

    def test_get_parents(self):
        parents = self.philip.parents()
        self.assertListEqual(self.gen1, parents)

    def test_get_gen_two(self):
        generation = self.philip.get_generation(2)
        self.assertListEqual(self.gen2, generation)

    def test_get_gen_one(self):
        generation = self.philip.get_generation(1)
        self.assertListEqual(self.gen1, generation)

    def test_get_gen_zero(self):
        generation = self.philip.get_generation(0)
        self.assertListEqual(self.gen0, generation)

    def test_get_gen_neg_one(self):
        generation = self.philip.get_generation(-1)
        self.assertListEqual(self.genN1, generation)

    def test_get_gen_neg_two(self):
        generation = self.philip.get_generation(-2)
        self.assertListEqual(self.genN2, generation)

    def test_get_siblings(self):
        expected = [self.akira]
        actual = self.colin.siblings()
        self.assertListEqual(expected, actual)

    def test_get_siblings_empty_list(self):
        expected = []
        actual = self.philip.siblings()
        self.assertListEqual(expected, actual)
