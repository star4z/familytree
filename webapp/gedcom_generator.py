from gedcom.element.element import Element
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

import webapp.tags_ext as tags
from webapp.models import *


def gen_head_and_submitter(tree):
    head_element = Element(0, '', tags.GEDCOM_TAG_HEAD, '')
    charset_element = Element(1, '', tags.GEDCOM_TAG_CHARSET, tags.GEDCOM_CHARSET_UTF8)
    head_element.add_child_element(charset_element)
    gedcom_element = Element(1, '', tags.GEDCOM_TAG_GEDCOM, '')
    version_element = Element(2, '', tags.GEDCOM_TAG_VERSION, '5.5')
    gedcom_element.add_child_element(version_element)
    format_element = Element(2, '', tags.GEDCOM_TAG_FORM, 'Lineage-Linked')
    gedcom_element.add_child_element(format_element)
    head_element.add_child_element(gedcom_element)

    if tree.creator is not None:
        submitter_ptr = '@SUBMITTER@'
        head_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_SUBMITTER, submitter_ptr))
        submitter_element = Element(0, submitter_ptr, tags.GEDCOM_TAG_SUBMITTER, '')
        submitter_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, tree.creator.username))
        return head_element, submitter_element
    else:
        return head_element, None


def gen_event(level, tag, date: datetime, location):
    event_element = Element(level, '', tag, '')
    if date:
        event_element.add_child_element(Element(level + 1, '', tags.GEDCOM_TAG_DATE, date.strftime("%d %b %Y").upper()))
    if location:
        event_element.add_child_element(Element(level + 1, '', tags.GEDCOM_TAG_PLACE, str(location)))
    return event_element


def gen_individual(person: Person):
    ptr = f"@PERSON_{person.id}@"
    individual_element = IndividualElement(0, ptr, tags.GEDCOM_TAG_INDIVIDUAL, '')

    legal_name = person.legal_name
    individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, legal_name.full_name()))
    if legal_name.prefix:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME_PREFIX, legal_name.prefix))
    individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_GIVEN_NAME, legal_name.first_name))
    if legal_name.last_name:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_SURNAME, legal_name.last_name))
    if legal_name.suffix:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME_SUFFIX, legal_name.suffix))

    for name in person.alternate_name.all():
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, name.full_name()))

    individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_SEX, person.gender_shorthand()))

    if person.birth_date or person.birth_location:
        individual_element.add_child_element(
            gen_event(1, tags.GEDCOM_TAG_BIRTH, person.birth_date, person.birth_location))

    if person.death_date or person.death_location:
        individual_element.add_child_element(
            gen_event(1, tags.GEDCOM_TAG_DEATH, person.death_date, person.death_location))

    for partnership in Partnership.objects.filter(person=person):
        individual_element.add_child_element(
            Element(1, '', tags.GEDCOM_TAG_FAMILY_SPOUSE, f'@PARTNERSHIP_{partnership.id}'))

    for partnership in Partnership.objects.filter(children=person):
        individual_element.add_child_element(
            Element(1, '', tags.GEDCOM_TAG_FAMILY_CHILD, f'@PARTNERSHIP_{partnership.id}'))

    return ptr, individual_element


def gen_family(partnership):
    ptr = f"@PARTNERSHIP_{partnership.id}@"
    family_element = Element(0, ptr, tags.GEDCOM_TAG_FAMILY, '')

    # todo

    return ptr, family_element


def generate_file(tree: Tree):
    parser = Parser()
    parser.parse([])
    root = parser.get_root_element()
    head_element, submitter_element = gen_head_and_submitter(tree)
    root.add_child_element(head_element)
    if submitter_element is not None:
        root.add_child_element(submitter_element)

    # individuals = dict()
    for person in Person.objects.filter(tree=tree):
        ptr, individual = gen_individual(person)
        # individuals[ptr] = individual
        root.add_child_element(individual)

    # families = dict()
    for partnership in Partnership.objects.filter(tree=tree):
        ptr, family = gen_family(partnership)
        # families[ptr] = family
        root.add_child_element(family)

    return root
