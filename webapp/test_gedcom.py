from django.test import TestCase

import webapp.tags_ext as tags
from webapp import gedcom_helpers, name_parser_ext
from webapp import gedcom_parsing
from webapp.models import *


def gen_individual():
    """
    0 @FATHER@ INDI
        1 NAME /Some/
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
    individual = gedcom_helpers.create_individual('@FATHER', '/Some/ Guy', 'M', 'city, state, US', '1 JAN 1899',
                                                  'city', '31 DEC 1990', '@FAMILY')

    return individual


class GedcomNameTestCase(TestCase):

    def test_split_name(self):
        parts = name_parser_ext.split_with_slash_support("/Tri Minh/ Doung")
        self.assertEqual(["Tri Minh", "Doung"], parts)
        parts = name_parser_ext.split_with_slash_support("/David/ /Gregory/ /Smith/")
        self.assertEqual(["David", "Gregory", "Smith"], parts)
        parts = name_parser_ext.split_with_slash_support("David /Gregory Smith/")
        self.assertEqual(["David", "Gregory Smith"], parts)
        parts = name_parser_ext.split_with_slash_support("David Gregory Smith")
        self.assertEqual(["David", "Gregory", "Smith"], parts)
        parts = name_parser_ext.split_with_slash_support("David /Gregory/ Smith")
        self.assertEqual(["David", "Gregory", "Smith"], parts)
        parts = name_parser_ext.split_with_slash_support("/David/ Gregory /Smith/")
        self.assertEqual(["David", "Gregory", "Smith"], parts)


class GedcomTestCase(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(title='test tree')

    def test_get_root(self):
        with open("gedcom_examples/simple.ged") as f:
            root = gedcom_parsing.get_root_element(f.buffer)
            self.assertIsNotNone(root)

    def test_filter_child_elements(self):
        name_elements = gedcom_helpers.filter_child_elements(gen_individual(), tags.GEDCOM_TAG_NAME)
        self.assertNotEqual(name_elements, [])

    def test_get_names(self):
        names = gedcom_helpers.get_names(gen_individual())
        name = next(names)
        expected = {'title': '', 'first': 'Some', 'middle': '', 'last': 'Guy', 'suffix': '', 'nickname': ''}
        self.assertDictEqual(name, expected)

    def test_parse_country(self):
        country = gedcom_parsing.parse_country("US")
        self.assertEqual(country, "US")
        country = gedcom_parsing.parse_country("United States")
        self.assertEqual(country, "US")
        country = gedcom_parsing.parse_country("UNITED_STATES")
        self.assertEqual(country, "US")

    def test_parse_gender(self):
        gender = gedcom_parsing.parse_gender("M")
        self.assertEqual(gender, "Male")
        gender = gedcom_parsing.parse_gender("F")
        self.assertEqual(gender, "Female")
        gender = gedcom_parsing.parse_gender("U")
        self.assertEqual(gender, "Unknown")

    def test_parse_event_location(self):
        event = gedcom_helpers.create_event(tags.GEDCOM_TAG_BIRTH, 'city, state, US', '12 JAN 1998')
        location = gedcom_parsing.parse_event_location(event)
        self.assertEqual(location.city, 'city')
        self.assertEqual(location.state, 'state')
        self.assertEqual(location.country, 'US')

    def test_parse_event_date(self):
        event = gedcom_helpers.create_event(tags.GEDCOM_TAG_BIRTH, 'city, state, US', '12 JAN 1998')
        date = gedcom_parsing.parse_event_date(event)
        self.assertEqual(date, datetime.date(1998, 1, 12))

    def test_parse_individual(self):
        individual = gen_individual()

        person = gedcom_parsing.parse_individual(individual, self.tree)
        self.assertEqual(person.legal_name.first_name, 'Some')
        self.assertEqual(person.legal_name.last_name, 'Guy')
        self.assertEqual(person.gender, 'Male')
        self.assertEqual(person.birth_date, datetime.date(1899, 1, 1))
        self.assertEqual(person.birth_location.city, 'city')
        self.assertEqual(person.birth_location.state, 'state')
        self.assertEqual(person.birth_location.country, 'US')
        self.assertEqual(person.death_date, datetime.date(1990, 12, 31))
        self.assertEqual(person.death_location.city, 'city')
        self.assertEqual(person.living, 'Unknown')

    def test_minimal_person(self):
        individual = gedcom_helpers.create_individual('@P1@', 'John Cho')

        person = gedcom_parsing.parse_individual(individual, self.tree)
        self.assertEqual(person.legal_name.first_name, 'John')
        self.assertEqual(person.legal_name.last_name, 'Cho')
        self.assertEqual(person.living, 'Unknown')
