from django.core.files.uploadedfile import UploadedFile
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser

from webapp.gedcom_helpers import *
from webapp.models import *


def parse_file(f: UploadedFile, user):
    parser = Parser()
    parser.parse(f)
    root = parser.get_root_element()
    for child_element in root.get_child_elements():
        if type(child_element) is IndividualElement:
            # noinspection PyTypeChecker
            parse_individual(child_element)
        elif type(child_element) is FamilyElement:
            # noinspection PyTypeChecker
            parse_family(child_element)
    parser.print_gedcom()


def parse_individual(element: IndividualElement):
    child = Person()

    # get names from element
    names = get_names(element)

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


def parse_name_dict(name_dict, obj: Name):
    prefix = name_dict['title']
    if prefix:
        obj.prefix = prefix
    first = name_dict['first']
    if first:
        obj.first_name = first
    middle = name_dict['middle']
    if middle:
        obj.middle_name = middle
    last = name_dict['last']
    if last:
        obj.last_name = last
    suffix = name_dict['suffix']
    if suffix:
        obj.suffix = suffix


def parse_family(element: FamilyElement):
    partnership = Partnership()
