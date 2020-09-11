from django.test import TestCase
from gedcom.element.element import Element

import webapp.tags_ext as tags
from webapp import gedcom_helpers, name_parser_ext
from webapp import gedcom_parsing
from webapp.models import *


def gen_individual():
    """
    0 @FATHER@ INDI
        1 NAME /Some/ Guy
        1 SEX M
        1 BIRT
            2 PLAC city, state, US
            2 DATE 1 JAN 1899
        1 DEAT
            2 PLAC city
            2 DATE 31 DEC 1990
        1 FAMS @FAMILY@
    :return:
    """
    individual = gedcom_helpers.create_individual('@FATHER', 0, '/Some/ Guy', 'M', 'city, state, US', '1 JAN 1899',
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
        individual = gen_individual()
        elements_with_name_tag = gedcom_helpers.filter_child_elements(individual, tag=tags.GEDCOM_TAG_NAME)
        for element in elements_with_name_tag:
            self.assertEqual(element.get_tag(), tags.GEDCOM_TAG_NAME)

        elements_with_name_value = gedcom_helpers.filter_child_elements(individual, value="/Some/ Guy")
        for element in elements_with_name_value:
            self.assertEqual(element.get_value(), '/Some/ Guy')

        # This is not a real case where a pointer would be used in GEDCOM, this is just for testing
        individual.add_child_element(Element(1, '@P1@', tags.GEDCOM_TAG_INDIVIDUAL, ''))
        elements_with_family_pointer = gedcom_helpers.filter_child_elements(individual, pointer="@P1@")
        for element in elements_with_family_pointer:
            self.assertEqual(element.get_pointer(), '@P1@')

        elements_with_tag_and_value = gedcom_helpers.filter_child_elements(individual, tag=tags.GEDCOM_TAG_SEX,
                                                                           value='M')
        for element in elements_with_tag_and_value:
            self.assertEqual(element.get_tag(), tags.GEDCOM_TAG_SEX)
            self.assertEqual(element.get_value(), 'M')

        match_tag_with_multiple_tags = gedcom_helpers \
            .filter_child_elements(individual, (tags.GEDCOM_TAG_NAME, tags.GEDCOM_TAG_SEX))
        for element in match_tag_with_multiple_tags:
            self.assertIn(element.get_tag(), (tags.GEDCOM_TAG_NAME, tags.GEDCOM_TAG_SEX))

        # tags should not be empty, and we know this is true for the example
        no_elements = gedcom_helpers.filter_child_elements(individual, tag="")
        self.assertEqual(no_elements, [])

        contains_tag = gedcom_helpers.filter_child_elements(individual, tag=True)
        for element in contains_tag:
            self.assertNotIn(element.get_tag(), ('', None))

        not_contains_value = gedcom_helpers.filter_child_elements(individual, value=False)
        for element in not_contains_value:
            self.assertIn(element.get_value(), ('', None))

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

        # Test to make sure trying to create a duplicate location is handled properly
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

        ptr, person = gedcom_parsing.parse_individual(individual, self.tree)
        self.assertEqual(person.legal_name.first_name, 'Some')
        self.assertEqual(person.legal_name.last_name, 'Guy')
        self.assertEqual(person.gender, 'Male')
        self.assertEqual(person.birth_date, datetime.date(1899, 1, 1))
        self.assertEqual(person.birth_location.city, 'city')
        self.assertEqual(person.birth_location.state, 'state')
        self.assertEqual(person.birth_location.country, 'US')
        self.assertEqual(person.death_date, datetime.date(1990, 12, 31))
        self.assertEqual(person.death_location.city, 'city')
        self.assertEqual(person.death_location.state, '')
        self.assertEqual(person.death_location.country, '')
        self.assertEqual(person.living, 'Unknown')

    def test_minimal_person(self):
        individual = gedcom_helpers.create_individual('@P1@', name='John Cho')

        ptr, person = gedcom_parsing.parse_individual(individual, self.tree)
        self.assertEqual(person.legal_name.first_name, 'John')
        self.assertEqual(person.legal_name.last_name, 'Cho')
        self.assertEqual(person.living, 'Unknown')

    def test_parse_family(self):
        legal_name_1 = LegalName(first_name='Spouse', last_name='1')
        legal_name_1.save()
        person_1 = Person(legal_name=legal_name_1)
        person_1.save()
        legal_name_2 = LegalName(first_name='Spouse', last_name='2')
        legal_name_2.save()
        person_2 = Person(legal_name=legal_name_2)
        person_2.save()
        legal_name_3 = LegalName(first_name='Child', last_name='1')
        legal_name_3.save()
        person_3 = Person(legal_name=legal_name_3)
        person_3.save()
        persons = {
            '@P1@': person_1,
            '@P2@': person_2,
            '@P3@': person_3
        }
        family_element = gedcom_helpers.create_family('@F1@',
                                                      husb_ptrs=('@P1@',),
                                                      wife_ptrs=('@P2@',),
                                                      child_ptrs=('@P3@',),
                                                      marriage_place="city, state, US",
                                                      marriage_date='13 JAN 1900',
                                                      divorce_date='14 JAN 1911')

        partnership = gedcom_parsing.parse_family(family_element, persons, self.tree)
        partners = tuple(p for p in partnership.partners())
        self.assertEqual(partners, (person_1, person_2))
        children = tuple(c for c in partnership.children.all())
        self.assertEqual(children, (person_3,))
        self.assertEqual(partnership.marriage_date, datetime.date(1900, 1, 13))
        self.assertEqual(partnership.divorce_date, datetime.date(1911, 1, 14))

    def test_parse_file(self):
        user = User(username="test_user", password="test_password")
        user.save()
        with open("gedcom_examples/simple.ged") as f:
            tree = gedcom_parsing.parse_file(f.buffer, user)
            self.assertIsNotNone(tree)
