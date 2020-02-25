from django.test import TestCase
from webapp import models


class PersonTestCase(TestCase):
    def setUp(self):
        tree = models.Tree.objects.create(title='test tree')
        partnerships = [self.create_partnership(tree) for _ in range(5)]
        persons = [
            self.create_person(tree, 'Abe', 'M', partnerships[0]),
            self.create_person(tree, 'Beth', 'F', partnerships[0]),
            self.create_person(tree, 'Dave', 'M', partnerships[1]),
            self.create_person(tree, 'Jeanine', 'F', partnerships[1]),
            self.create_person(tree, 'Philip', 'M', partnerships[2]),
            self.create_person(tree, 'Megumi', 'F', partnerships[2]),
            self.create_person(tree, 'Akito', 'M', partnerships[3]),
            self.create_person(tree, 'Nala', 'F', partnerships[3]),
            self.create_person(tree, 'Colin', 'M'),
            self.create_person(tree, 'Akira', 'F'),
            self.create_person(tree, 'Elizabeth', 'F', partnerships[4]),
            self.create_person(tree, 'Kassandra', 'F', partnerships[4]),
            self.create_person(tree, 'John', 'M'),
            self.create_person(tree, 'Violet', 'F'),
        ]

        partnerships[0].children.add(persons[2])  # Dave is Abe and Beth's child
        partnerships[1].children.add(persons[4])  # Philip is Dave and Jeanine's child
        partnerships[2].children.add(persons[6])  # Akito is Philip and Megumi's child
        partnerships[3].children.add(persons[8])  # Colin is Akito and Nala's child
        partnerships[3].children.add(persons[9])  # Akira is Akito and Nala's child
        partnerships[2].children.add(persons[10])  # Elizabeth is Philip and Megumi's child
        partnerships[4].children.add(persons[12])  # John is Elizabeth and Kassandra's child
        partnerships[4].children.add(persons[13])  # Violet is Elizabeth and Kassandra's child

        self.person = persons[4]

        self.gen2 = partnerships[0:1]
        self.gen1 = partnerships[1:2]
        self.gen0 = persons[4:5]
        self.genN1 = persons[6:7] + persons[10:11]
        self.genN2 = persons[8:10] + persons[12:]

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

    def test_get_gen_two(self):
        generation = list(self.person.get_generation(2).all())
        self.assertListEqual(self.gen2, generation)

    def test_get_gen_one(self):
        generation = list(self.person.get_generation(1).all())
        self.assertListEqual(self.gen1, generation)

    def test_get_gen_zero(self):
        generation = list(self.person.get_generation(0).all())
        self.assertListEqual(self.gen0, generation)

    def test_get_gen_neg_one(self):
        generation = list(self.person.get_generation(-1).all())
        self.assertListEqual(self.genN1, generation)

    def test_get_gen_neg_two(self):
        generation = list(self.person.get_generation(-2).all())
        self.assertListEqual(self.genN2, generation)
