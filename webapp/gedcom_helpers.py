from gedcom.element.element import Element
from gedcom.element.individual import IndividualElement

import webapp.tags_ext as tags
from webapp.name_parser_ext import GedcomName


def get_next_child_element(self: Element, tag=None, pointer=None, value=None):
    return next(filter_child_elements(self, tag, pointer, value), None)


def filter_child_elements(self: Element, tag=None, pointer=None, value=None):
    """
    Gets all the child elements of the given element that meet the given conditions.
    When no conditions are specified, all child elements are returned.
    Passing True to a filter returns all elements that have a value for that filter that is not None or empty.
    Passing False to a filter returns all elements that have a value for that filter that is None or empty.
    Passing a str to a filter returns all elements that have a value for that filter that is equal to the filter.
    Passing a set, list, or tuple to a filter returns all elements that have a value contained in the filter.
    :param self: Element to search
    :param tag: tag filter
    :param pointer: pointer filter
    :param value: value filter
    :return: a list of all child elements matching the filters
    """

    def condition(value_to_match, value_to_check):
        if value_to_match is None:
            return True
        elif isinstance(value_to_match, bool):
            return bool(value_to_check) == value_to_match
        elif isinstance(value_to_match, str):
            return value_to_check == value_to_match
        elif isinstance(value_to_match, (list, tuple, set)):
            return value_to_check in value_to_match
        else:
            return False

    return [child for child in self.get_child_elements()
            if condition(tag, child.get_tag())
            and condition(pointer, child.get_pointer())
            and condition(value, child.get_value())]


def get_name(self: IndividualElement):
    name = get_next_child_element(self, tag=tags.GEDCOM_TAG_NAME)
    if name is not None:
        return GedcomName(name.get_value()).as_dict()
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
    :param self:
    :return: tuple of dicts of name parts for each name
    """
    names = filter_child_elements(self, tag=tags.GEDCOM_TAG_NAME)
    if names:
        return (GedcomName(name.get_value()).as_dict() for name in names)
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
