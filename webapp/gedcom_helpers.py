from gedcom.element.element import Element
from gedcom.element.individual import IndividualElement
from webapp.name_parser_ext import *

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
            if (tag is None or child.get_tag() == tag)
            and (pointer is None or child.get_pointer() == pointer)
            and (value is None or child.get_value() == value)]


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


def get_value(self: Element, tag: str):
    """
    Gets the value of a child with the given tag
    :param self: Element whose children will be searched
    :param tag: tag to look for
    :return: the value of child with the given tag, else empty string
    """
    for child in self.get_child_elements():
        if child.get_tag() == tag:
            return child.get_value()

    return ""


def create_individual(ptr: str,
                      name: str = None,
                      sex: str = None,
                      birth_place: str = None,
                      birth_date: str = None,
                      death_place: str = None,
                      death_date: str = None,
                      family_spouse_ptr: str = None,
                      family_child_ptr: str = None):
    individual_element = IndividualElement(0, ptr, tags.GEDCOM_TAG_INDIVIDUAL, '')
    if name is not None:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_NAME, name))
    if sex is not None:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_SEX, sex))
    if birth_place is not None and birth_date is not None:
        individual_element.add_child_element(create_event(tags.GEDCOM_TAG_BIRTH, birth_place, birth_date))
    if death_place is not None and death_date is not None:
        individual_element.add_child_element(create_event(tags.GEDCOM_TAG_DEATH, death_place, death_date))
    if family_spouse_ptr is not None:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_FAMILY_SPOUSE, family_spouse_ptr))
    if family_child_ptr is not None:
        individual_element.add_child_element(Element(1, '', tags.GEDCOM_TAG_FAMILY_CHILD, family_child_ptr))
    return individual_element


def create_event(tag_type: str, place: str, date: str):
    event_element = Element(1, '', tag_type, '')
    event_place_element = Element(2, '', tags.GEDCOM_TAG_PLACE, place)
    event_element.add_child_element(event_place_element)
    event_date_element = Element(2, '', tags.GEDCOM_TAG_DATE, date)
    event_element.add_child_element(event_date_element)
    return event_element
