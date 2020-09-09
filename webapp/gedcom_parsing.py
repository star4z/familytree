from typing import Dict

from django.core.files.uploadedfile import UploadedFile
from gedcom.parser import Parser

from webapp.gedcom_helpers import *
from webapp.models import *


def parse_file(f: UploadedFile, user):
    root = get_root_element(f)

    tree = Tree()

    persons = dict()
    family_elements = list()
    for child_element in root.get_child_elements():
        if type(child_element) is IndividualElement:
            # noinspection PyTypeChecker
            ptr, person = parse_individual(child_element, tree)
            persons[ptr] = person
        elif type(child_element) is FamilyElement:
            family_elements.append(child_element)

    for family_element in family_elements:
        # noinspection PyTypeChecker
        partnership = parse_family(family_element, persons, tree)

    # tree.save()


def get_root_element(f):
    parser = Parser()
    parser.parse(f)
    root = parser.get_root_element()
    return root


def parse_event_date(event_element):
    date = get_value(event_element, tags.GEDCOM_TAG_DATE)
    # TODO: Support other date formats. Some require alternate date storage formats, like a custom string, or a range.
    return datetime.datetime.strptime(date, "%d %b %Y").date()


def parse_event_location(event_element):
    place = get_value(event_element, tags.GEDCOM_TAG_PLACE)
    parts = place.split(' ')
    location = Location()

    len_parts = len(parts)
    if len_parts >= 1:
        location.city = parts[0].strip(',')
    if len_parts >= 2:
        location.state = parts[1].strip(',')
    if len_parts >= 3:
        location.country = parse_country(parts[2])

    location.save()

    return location


def parse_country(country):
    if country in Location.Country.names:
        return Location.Country[country].value

    for choice in Location.Country.choices:
        if country in choice:
            return choice[0]
    return None


def parse_individual(element: IndividualElement, tree):
    child = Person()

    # get names from element
    names = list(get_names(element))

    # save legal name
    # assumes first name in list is primary name
    legal_name = LegalName()
    parse_name_dict(names[0], legal_name)
    legal_name.save()
    child.legal_name = legal_name

    # save alternate names
    for name_dict in names[1:]:
        alternate_name = AlternateName()
        parse_name_dict(name_dict, alternate_name)
        alternate_name.person = child
        alternate_name.save()

    child.gender = parse_gender(get_value(element, tags.GEDCOM_TAG_SEX))

    # Is saving related models necessary, or will it cascade?
    birth_event_element = get_next_child_element(element, tags.GEDCOM_TAG_BIRTH)
    if birth_event_element:
        child.birth_date = parse_event_date(birth_event_element)
        child.birth_location = parse_event_location(birth_event_element)

    death_event_element = get_next_child_element(element, tags.GEDCOM_TAG_DEATH)
    if death_event_element:
        child.death_date = parse_event_date(death_event_element)
        child.death_location = parse_event_location(death_event_element)

    # living defaults to Unknown; change to living = has birth year and not has death year?

    child.tree = tree

    child.save()

    return element.get_pointer(), child


def parse_name_dict(name_dict, obj: Name):
    if 'title' in name_dict:
        obj.prefix = name_dict['title']
    if 'first' in name_dict:
        obj.first_name = name_dict['first']
    if 'middle' in name_dict:
        obj.middle_name = name_dict['middle']
    if 'last' in name_dict:
        obj.last_name = name_dict['last']
    if 'suffix' in name_dict:
        obj.suffix = name_dict['suffix']


def parse_family(element: FamilyElement, persons: Dict[str, Person], tree):
    partnership = Partnership()

    partnership.marital_status = Partnership.MaritalStatus.PARTNERED

    marriage_event_element = get_next_child_element(element, tag=tags.GEDCOM_TAG_MARRIAGE)
    if marriage_event_element:
        partnership.marital_status = Partnership.MaritalStatus.MARRIED
        partnership.marriage_date = parse_event_date(marriage_event_element)
        # TODO: add support for storing marriage location

    divorce_event_element = get_next_child_element(element, tag=tags.GEDCOM_TAG_DIVORCE)
    if divorce_event_element:
        partnership.marital_status = Partnership.MaritalStatus.DIVORCED
        partnership.divorce_date = parse_event_date(divorce_event_element)

    partnership.tree = tree

    partnership.save()

    # Create partner relations
    for partner_element in filter_child_elements(element, tag=(tags.GEDCOM_TAG_HUSBAND, tags.GEDCOM_TAG_WIFE)):
        person_partnership = PersonPartnership(partnership=partnership, person=persons[partner_element.get_value()])
        person_partnership.save()

    # Create children relations
    partnership_children = Partnership.children.through
    for child_element in filter_child_elements(element, tag=tags.GEDCOM_TAG_CHILD):
        relation = partnership_children(partnership=partnership)
        relation.person = persons[child_element.get_value()]
        relation.save()

    return partnership


def parse_gender(gender: str):
    # Intersex and Other are unsupported by the GEDCOM standard
    if gender == 'M':
        return 'Male'
    elif gender == 'F':
        return 'Female'
    elif gender == 'I':
        return 'Intersex'
    elif gender == 'O':
        return 'Other'
    else:
        return 'Unknown'
