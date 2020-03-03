from django.test import TestCase
from webapp import models


class PersonTestCase(TestCase):
    def setUp(self):
        self.tree = models.Tree.objects.create(title='test tree')

        self.abe = self.create_person('Abe', 'M', [1])
        self.beth = self.create_person('Beth', 'F', [1])
        self.dave = self.create_person('Dave', 'M', [2])
        self.jeanine = self.create_person('Jeanine', 'F', [2])
        self.philip = self.create_person('Philip', 'M', [3])
        self.megumi = self.create_person('Megumi', 'F', [3])
        self.akito = self.create_person('Akito', 'M', [4])
        self.nala = self.create_person('Nala', 'F', [4])
        self.colin = self.create_person('Colin', 'M')
        self.akira = self.create_person('Akira', 'F')
        self.elizabeth = self.create_person('Elizabeth', 'F', [5])
        self.kassandra = self.create_person('Kassandra', 'F', [5])
        self.john = self.create_person('John', 'M')
        self.violet = self.create_person('Violet', 'F')
        self.pablo = self.create_person('Pablo', 'M', )

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

    def create_person(self, first_name, gender, partnership_ids=None):
        genders = {'M': 'Male', 'F': 'Female'}
        legal_name = models.LegalName.objects.create(first_name=first_name)
        legal_name.save()
        p = models.Person.objects.create(tree=self.tree, legal_name=legal_name, gender=genders[gender])
        p.save()
        if partnership_ids:
            for pid in partnership_ids:
                partnership = self.get_partnership(pid)
                person_partnership = models.PersonPartnership.objects.create(person=p, partnership=partnership)
                person_partnership.save()
        return p

    def get_partnership(self, pid):
        partnership, created = models.Partnership.objects.get_or_create(id=pid, defaults={'tree': self.tree})
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
