from django.core.files.uploadedfile import UploadedFile
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser

from webapp.gedcom_helpers import *
from webapp.models import *


def parse_file(f: UploadedFile, user):
    root = get_root_element(f)

    tree = Tree()

    for child_element in root.get_child_elements():
        if type(child_element) is IndividualElement:
            # noinspection PyTypeChecker
            child = parse_individual(child_element, tree)
        elif type(child_element) is FamilyElement:
            # noinspection PyTypeChecker
            child = parse_family(child_element, tree)

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
    child.birth_date = parse_event_date(birth_event_element)
    child.birth_location = parse_event_location(birth_event_element)

    death_event_element = get_next_child_element(element, tags.GEDCOM_TAG_DEATH)
    child.death_date = parse_event_date(death_event_element)
    child.death_location = parse_event_location(death_event_element)

    return child


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


def parse_family(element: FamilyElement, tree):
    partnership = Partnership()

    partnership.tree = tree

    return partnership


def parse_gender(gender: str):
    # Intersex and Other are technically unsupported by the GEDCOM standard
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
