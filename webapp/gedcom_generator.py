from gedcom.element.element import Element
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


def generate_file(tree: Tree):
    parser = Parser()
    parser.parse([])
    root = parser.get_root_element()
    head_element, submitter_element = gen_head_and_submitter(tree)
    root.add_child_element(head_element)
    if submitter_element is not None:
        root.add_child_element(submitter_element)
