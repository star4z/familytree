from gedcom.element.element import Element


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
