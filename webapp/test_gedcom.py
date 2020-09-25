import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from gedcom.element.element import Element
from gedcom.parser import Parser

import webapp.tags_ext as tags
from webapp import gedcom_helpers, name_parser_ext, gedcom_generator
from webapp import gedcom_parsing
from webapp.models import Tree, LegalName, Person, AlternateName, Partnership, PersonPartnership
from webapp.submodels.location_model import Location


def gen_test_individual():
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

    def test_parse_name(self):
        self.assertEqual(name_parser_ext.GedcomName("Henry Ford").as_dict(False), {'first': 'Henry', 'last': 'Ford'})
        self.assertEqual(name_parser_ext.GedcomName("Robert Louis Stevenson").as_dict(False),
                         {'first': 'Robert', 'middle': 'Louis', 'last': 'Stevenson'})
        self.assertEqual(name_parser_ext.GedcomName("Dr. Martin Luther King, Jr.").as_dict(False),
                         {'title': 'Dr', 'first': 'Martin', 'middle': 'Luther', 'last': 'King', 'suffix': 'Jr.'})


class GedcomTestCase(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(title='test tree')

    def test_get_root(self):
        with open("gedcom_examples/simple.ged") as f:
            root = gedcom_parsing.get_root_element(f.buffer)
            self.assertIsNotNone(root)

    def test_filter_child_elements(self):
        individual = gen_test_individual()
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
        names = gedcom_helpers.get_names(gen_test_individual())
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
        individual = gen_test_individual()

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
        self.assertEqual(person.living, 'Dead')

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
            tree = gedcom_parsing.parse_file(f.buffer, user, 'Tree')
            self.assertIsNotNone(tree)

    def test_gen_individual(self):
        birth_date = datetime.datetime(1980, 1, 1)
        death_date = datetime.datetime(2040, 1, 1)
        legal_name = LegalName(first_name="David", last_name="Schmidt")
        legal_name.save()
        birth_location = Location(city='New York', state='NY', country='US')
        birth_location.save()
        death_location = Location(city='Boston', state='MA', country='US')
        death_location.save()
        person = Person(
            legal_name=legal_name,
            gender="Male",
            birth_date=birth_date,
            birth_location=birth_location,
            death_date=death_date,
            death_location=death_location,
        )
        person.save()
        alternate_name = AlternateName(first_name='Lance', last_name='Springer', person=person)
        alternate_name.save()

        partner_partnership = Partnership()
        partner_partnership.save()

        person_partnership = PersonPartnership(person=person, partnership=partner_partnership)
        person_partnership.save()

        child_partnership = Partnership()
        child_partnership.save()
        child_partnership.children.add(person)

        ptr, individual = gedcom_generator.gen_individual(person)
        expected = gedcom_helpers.create_individual(f"@PERSON_{person.id}@",
                                                    name="David Schmidt",
                                                    sex='M',
                                                    birth_place='New York, NY, US',
                                                    birth_date=birth_date.strftime("%d %b %Y").upper(),
                                                    death_place='Boston, MA, US',
                                                    death_date=death_date.strftime("%d %b %Y").upper())
        expected.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, 'Lance Springer'))
        expected.add_child_element(Element(1, '', tags.GEDCOM_TAG_GIVEN_NAME, 'David'))
        expected.add_child_element(Element(1, '', tags.GEDCOM_TAG_SURNAME, 'Schmidt'))
        expected.add_child_element(Element(1, '', tags.GEDCOM_TAG_FAMILY_SPOUSE,
                                           f'@PARTNERSHIP_{partner_partnership.id}@'))
        expected.add_child_element(Element(1, '', tags.GEDCOM_TAG_FAMILY_CHILD,
                                           f'@PARTNERSHIP_{child_partnership.id}@'))

        self.assertTrue(gedcom_helpers.element_equals(individual, expected))

    def test_gen_family(self):
        spouse_1_legal_name = LegalName(first_name="Betty")
        spouse_1_legal_name.save()
        spouse_1 = Person(legal_name=spouse_1_legal_name, gender='Female')
        spouse_1.save()
        spouse_2_legal_name = LegalName(first_name="Kyle")
        spouse_2_legal_name.save()
        spouse_2 = Person(legal_name=spouse_2_legal_name, gender='Male')
        spouse_2.save()
        child_legal_name = LegalName(first_name="Symphony")
        child_legal_name.save()
        child = Person(legal_name=child_legal_name)
        child.save()
        marriage_date = datetime.datetime(2000, 12, 1)
        divorce_date = datetime.datetime(2100, 12, 2)
        partnership = Partnership(marriage_date=marriage_date,
                                  divorce_date=divorce_date,
                                  marital_status=Partnership.MaritalStatus.MARRIED)
        partnership.save()
        partnership.children.add(child)
        partnership.save()
        person_partnership_1 = PersonPartnership(person=spouse_1, partnership=partnership)
        person_partnership_1.save()
        person_partnership_2 = PersonPartnership(person=spouse_2, partnership=partnership)
        person_partnership_2.save()

        ptr, family_element = gedcom_generator.gen_family(partnership)

        expected = gedcom_helpers.create_family(gedcom_helpers.gen_ptr(partnership),
                                                husb_ptrs=(gedcom_helpers.gen_ptr(spouse_2),),
                                                wife_ptrs=(gedcom_helpers.gen_ptr(spouse_1),),
                                                child_ptrs=(gedcom_helpers.gen_ptr(child),),
                                                marriage_date=gedcom_helpers.gedcom_date(marriage_date),
                                                divorce_date=gedcom_helpers.gedcom_date(divorce_date))

        self.assertTrue(gedcom_helpers.element_equals(family_element, expected))

    def test_gen_same_sex_family(self):
        spouse_1_legal_name = LegalName(first_name="Betty")
        spouse_1_legal_name.save()
        spouse_1 = Person(legal_name=spouse_1_legal_name, gender='Female')
        spouse_1.save()
        spouse_2_legal_name = LegalName(first_name="Sally")
        spouse_2_legal_name.save()
        spouse_2 = Person(legal_name=spouse_2_legal_name, gender='Female')
        spouse_2.save()
        marriage_date = datetime.datetime(2000, 12, 1)
        divorce_date = datetime.datetime(2100, 12, 2)
        partnership = Partnership(marriage_date=marriage_date,
                                  divorce_date=divorce_date,
                                  marital_status=Partnership.MaritalStatus.MARRIED)
        partnership.save()
        person_partnership_1 = PersonPartnership(person=spouse_1, partnership=partnership)
        person_partnership_1.save()
        person_partnership_2 = PersonPartnership(person=spouse_2, partnership=partnership)
        person_partnership_2.save()

        ptr, family_element = gedcom_generator.gen_family(partnership)

        expected = gedcom_helpers.create_family(gedcom_helpers.gen_ptr(partnership),
                                                wife_ptrs=(gedcom_helpers.gen_ptr(spouse_1),
                                                           gedcom_helpers.gen_ptr(spouse_2)),
                                                marriage_date=gedcom_helpers.gedcom_date(marriage_date),
                                                divorce_date=gedcom_helpers.gedcom_date(divorce_date))

        self.assertTrue(gedcom_helpers.element_equals(family_element, expected))

    def test_gen_min_family(self):
        partnership = Partnership()
        partnership.save()
        ptr, family_element = gedcom_generator.gen_family(partnership)

        expected = gedcom_helpers.create_family(gedcom_helpers.gen_ptr(partnership))

        self.assertTrue(gedcom_helpers.element_equals(family_element, expected))

    def test_gen_head_and_submitter(self):
        user = User(username="steve")
        tree = Tree(title="Test", creator=user)

        head, submitter = gedcom_generator.gen_head_and_submitter(tree)

        expected_head = Element(0, '', tags.GEDCOM_TAG_HEAD, '')
        charset_element = Element(1, '', tags.GEDCOM_TAG_CHARSET, tags.GEDCOM_CHARSET_UTF8)
        expected_head.add_child_element(charset_element)
        gedcom_element = Element(1, '', tags.GEDCOM_TAG_GEDCOM, '')
        version_element = Element(2, '', tags.GEDCOM_TAG_VERSION, '5.5')
        gedcom_element.add_child_element(version_element)
        format_element = Element(2, '', tags.GEDCOM_TAG_FORM, 'Lineage-Linked')
        gedcom_element.add_child_element(format_element)
        expected_head.add_child_element(gedcom_element)
        submitter_ptr = '@SUBMITTER@'
        expected_head.add_child_element(Element(1, '', tags.GEDCOM_TAG_SUBMITTER, submitter_ptr))
        expected_submitter = Element(0, submitter_ptr, tags.GEDCOM_TAG_SUBMITTER, '')
        expected_submitter.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, tree.creator.username))

        self.assertTrue(gedcom_helpers.element_equals(head, expected_head))
        self.assertTrue(gedcom_helpers.element_equals(submitter, expected_submitter))

    def test_gen_file(self):
        user = User(username="example")
        user.save()
        tree = Tree(title="Test", creator=user)
        tree.save()
        spouse_1_legal_name = LegalName(first_name="Betty", tree=tree)
        spouse_1_legal_name.save()
        spouse_1 = Person(legal_name=spouse_1_legal_name, gender='Female', tree=tree)
        spouse_1.save()
        spouse_2_legal_name = LegalName(first_name="Kyle", tree=tree)
        spouse_2_legal_name.save()
        spouse_2 = Person(legal_name=spouse_2_legal_name, gender='Male', tree=tree)
        spouse_2.save()
        child_legal_name = LegalName(first_name="Symphony", tree=tree)
        child_legal_name.save()
        child = Person(legal_name=child_legal_name, gender="Unknown", tree=tree)
        child.save()
        marriage_date = datetime.datetime(2000, 12, 1)
        divorce_date = datetime.datetime(2100, 12, 2)
        partnership = Partnership(marriage_date=marriage_date,
                                  divorce_date=divorce_date,
                                  marital_status=Partnership.MaritalStatus.MARRIED,
                                  tree=tree)
        partnership.save()
        partnership.children.add(child)
        partnership.save()
        person_partnership_1 = PersonPartnership(person=spouse_1, partnership=partnership)
        person_partnership_1.save()
        person_partnership_2 = PersonPartnership(person=spouse_2, partnership=partnership)
        person_partnership_2.save()

        root = gedcom_generator.generate_file(tree)

        parser = Parser()
        parser.parse([])
        expected = parser.get_root_element()
        head_element, submitter_element = gedcom_generator.gen_head_and_submitter(tree)
        expected.add_child_element(head_element)
        expected.add_child_element(submitter_element)
        ptr, spouse_1_element = gedcom_generator.gen_individual(spouse_1)
        expected.add_child_element(spouse_1_element)
        ptr, spouse_2_element = gedcom_generator.gen_individual(spouse_2)
        expected.add_child_element(spouse_2_element)
        ptr, child_element = gedcom_generator.gen_individual(child)
        expected.add_child_element(child_element)
        ptr, family = gedcom_generator.gen_family(partnership)
        expected.add_child_element(family)

        self.assertTrue(gedcom_helpers.element_equals(root, expected))


class GedcomHelpersTest(TestCase):
    def test_element_values_equals(self):
        element_1 = Element(1, '', '', '')
        element_2 = Element(2, '', '', '')
        self.assertFalse(gedcom_helpers.element_values_equals(element_1, element_2))
        element_3 = Element(1, '', '', '')
        self.assertTrue(gedcom_helpers.element_values_equals(element_1, element_3))
        self.assertFalse(gedcom_helpers.element_values_equals(element_2, element_3))
        element_4 = Element(2, '', '', 'value')
        self.assertFalse(gedcom_helpers.element_values_equals(element_2, element_4))
        element_5 = Element(2, 'pointer', '', '')
        self.assertFalse(gedcom_helpers.element_values_equals(element_2, element_5))
        element_6 = Element(2, '', 'tag', '')
        self.assertFalse(gedcom_helpers.element_values_equals(element_2, element_6))
        element_7 = Element(2, 'pointer', 'tag', 'value')
        self.assertFalse(gedcom_helpers.element_values_equals(element_2, element_7))

    def test_gen_pointer(self):
        legal_name = LegalName(first_name="Chris")
        legal_name.save()
        legal_name_ptr = gedcom_helpers.gen_ptr(legal_name)
        self.assertEqual(legal_name_ptr, f"@LEGALNAME_{legal_name.pk}@")

        person = Person(legal_name=legal_name)
        person.save()
        person_ptr = gedcom_helpers.gen_ptr(person)
        self.assertEqual(person_ptr, f"@PERSON_{person.pk}@")

        partnership = Partnership()
        partnership.save()
        partnership_ptr = gedcom_helpers.gen_ptr(partnership)
        self.assertEqual(partnership_ptr, f"@PARTNERSHIP_{partnership.pk}@")
