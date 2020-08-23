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
