from gedcom.element.element import Element

import commons.gedcom.gedcom_helpers as helpers
import commons.gedcom.tags_ext as tags


class GedcomElement(Element):
    def get_tag(self):
        return tags.GEDCOM_TAG_GEDCOM

    def get_version(self):
        return helpers.get_value(self, tags.GEDCOM_TAG_VERSION)

    def get_form(self):
        return helpers.get_value(self, tags.GEDCOM_TAG_FORM)


class HeaderElement(Element):

    def get_tag(self):
        return tags.GEDCOM_TAG_HEAD

    def get_charset(self):
        """
        Returns the charset of a file
        """
        return helpers.get_value(self, tags.GEDCOM_TAG_CHARSET)

    def get_gedcom_data(self):
        return helpers.get_next_child_element(self, tag=tags.GEDCOM_TAG_GEDCOM)

    def get_submitter_ptr(self):
        return helpers.get_value(self, tags.GEDCOM_TAG_SUBMITTER)


class EventElement(Element):
    def get_date(self):
        return helpers.get_value(self, tags.GEDCOM_TAG_DATE)

    def get_place(self):
        return helpers.get_value(self, tags.GEDCOM_TAG_PLACE)
