from django.test import TestCase
from gedcom.element.element import Element
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

from webapp import gedcom_parsing
import webapp.tags_ext as tags
from webapp import gedcom_helpers
from webapp.models import *


def gen_individual():
    """
    0 @FATHER@ INDI
        1 NAME /Father/
        1 SEX M
        1 BIRT
            2 PLAC birth place
            2 DATE 1 JAN 1899
        1 DEAT
            2 PLAC death place
            2 DATE 31 DEC 1990
        1 FAMS @FAMILY@
    :return:
    """
    individual = gedcom_helpers.create_individual('@FATHER', '/Father/ Guy', 'M', 'birth place', '1 JAN 1899',
                                                  'death_place', '31 DEC 1990', '@FAMILY')

    return individual


class GedcomTestCase(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(title='test tree')

    def test_get_root(self):
        with open("webapp/simple.ged") as f:
            root = gedcom_parsing.get_root_element(f.buffer)
            self.assertIsNotNone(root)

    def test_filter_child_elements(self):
        name_elements = gedcom_helpers.filter_child_elements(gen_individual(), tags.GEDCOM_TAG_NAME)
        self.assertNotEqual(name_elements, [])

    def test_get_names(self):
        names = gedcom_helpers.get_names(gen_individual())
        name = next(names)
        self.assertDictEqual(name, {'first': 'Father', 'last': 'Guy'})

    def test_parse_individual(self):
        individual = gen_individual()

        person = gedcom_parsing.parse_individual(individual, self.tree)
        self.assertEqual(person.legal_name.first_name, 'Father')
