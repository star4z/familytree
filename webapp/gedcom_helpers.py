from gedcom.element.element import Element
from gedcom.element.individual import IndividualElement
from nameparser import HumanName

import webapp.tags_ext as tags


def get_next_child_element(self: Element, tag: str = None, pointer: str = None, value: str = None):
    return next((child for child in self.get_child_elements()
                 if (pointer is None or child.get_pointer() == pointer)
                 and (tag is None or child.get_tag() == tag)
                 and (value is None or child.get_value() == value))
                , None)


Element.get_next_child_element = get_next_child_element


def filter_child_elements(self: Element, tag: str = None, pointer: str = None, value: str = None):
    return [child for child in self.get_child_elements()
            if (pointer is not None and child.get_pointer() == pointer)
            and (tag is not None and child.get_tag() == tag)
            and (value is not None and child.get_value() == value)]


Element.filter_child_elements = filter_child_elements


def get_name(self: IndividualElement):
    name = get_next_child_element(self, tag=tags.GEDCOM_TAG_NAME)
    if name is not None:
        return HumanName(name.get_value()).as_dict()
    return get_name_dict_from_name_tags(self)


def get_name_dict_from_name_tags(self):
    name_dict = {}
    prefix = get_next_child_element(self, tag=tags.GEDCOM_TAG_NAME_PREFIX)
    if prefix:
        name_dict['title'] = prefix
    given_name = get_next_child_element(self, tag=tags.GEDCOM_TAG_GIVEN_NAME)
    if given_name:
        name_dict['first'] = given_name
    last_name = ''
    surname_prefix = get_next_child_element(self, tag=tags.GEDCOM_TAG_SURNAME_PREFIX)
    if surname_prefix:
        last_name += surname_prefix
    surname = get_next_child_element(self, tag=tags.GEDCOM_TAG_SURNAME)
    if surname:
        last_name += surname
    name_dict['last'] = surname
    suffix = get_next_child_element(self, tag=tags.GEDCOM_TAG_NAME_SUFFIX)
    if suffix:
        name_dict['suffix'] = suffix
    return name_dict


def get_names(self: IndividualElement):
    """
    Gets names from element.
    Assumes the first name in order is the primary name.
    :param self:
    :return: tuple of dicts of name parts for each name
    """
    names = filter_child_elements(self, tag=tags.GEDCOM_TAG_NAME)
    if names:
        return (HumanName(name.get_value()).as_dict() for name in names)
    return get_name_dict_from_name_tags(self),
