import shlex

from nameparser.parser import *


def parse_full_name(self):
    """

    The main parse method for the parser. This method is run upon
    assignment to the :py:attr:`full_name` attribute or instantiation.

    Basic flow is to hand off to :py:func:`pre_process` to handle
    nicknames. It then splits on commas and chooses a code path depending
    on the number of commas.

    :py:func:`parse_pieces` then splits those parts on spaces and
    :py:func:`join_on_conjunctions` joins any pieces next to conjunctions.
    """

    self.title_list = []
    self.first_list = []
    self.middle_list = []
    self.last_list = []
    self.suffix_list = []
    self.nickname_list = []
    self.unparsable = True

    self.pre_process()

    self._full_name = self.collapse_whitespace(self._full_name)

    # break up full_name by commas
    parts = [x.strip() for x in self._full_name.split(",")]

    log.debug("full_name: %s", self._full_name)
    log.debug("parts: %s", parts)

    if len(parts) == 1:

        # no commas, title first middle middle middle last suffix
        #            part[0]

        pieces = self.parse_pieces(parts)
        p_len = len(pieces)
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            # title must have a next piece, unless it's just a title
            if self.is_title(piece) \
                    and (nxt or p_len == 1) \
                    and not self.first:
                self.title_list.append(piece)
                continue
            if not self.first:
                if p_len == 1 and self.nickname:
                    self.last_list.append(piece)
                    continue
                self.first_list.append(piece)
                continue
            if self.are_suffixes(pieces[i + 1:]) or \
                    (
                            # if the next piece is the last piece and a roman
                            # numeral but this piece is not an initial
                            self.is_roman_numeral(nxt) and i == p_len - 2
                            and not self.is_an_initial(piece)
                    ):
                self.last_list.append(piece)
                self.suffix_list += pieces[i + 1:]
                break
            if not nxt:
                self.last_list.append(piece)
                continue

            self.middle_list.append(piece)
    else:
        # if all the end parts are suffixes and there is more than one piece
        # in the first part. (Suffixes will never appear after last names
        # only, and allows potential first names to be in suffixes, e.g.
        # "Johnson, Bart"

        lex = shlex.shlex(parts[1], posix=True)
        lex.quotes = "/"
        post_comma_pieces = self.parse_pieces(list(iter(lex.get_token, None)), 1)

        lex = shlex.shlex(parts[0], posix=True)
        lex.quotes = "/"
        parts0 = list(iter(lex.get_token, None))
        if self.are_suffixes(parts[1].split(' ')) \
                and len(parts0) > 1:

            # suffix comma:
            # title first middle last [suffix], suffix [suffix] [, suffix]
            #               parts[0],          parts[1:...]

            self.suffix_list += parts[1:]
            pieces = self.parse_pieces(parts0)
            log.debug("pieces: %s", u(pieces))
            for i, piece in enumerate(pieces):
                try:
                    nxt = pieces[i + 1]
                except IndexError:
                    nxt = None

                if self.is_title(piece) \
                        and (nxt or len(pieces) == 1) \
                        and not self.first:
                    self.title_list.append(piece)
                    continue
                if not self.first:
                    self.first_list.append(piece)
                    continue
                if self.are_suffixes(pieces[i + 1:]):
                    self.last_list.append(piece)
                    self.suffix_list = pieces[i + 1:] + self.suffix_list
                    break
                if not nxt:
                    self.last_list.append(piece)
                    continue
                self.middle_list.append(piece)
        else:

            # lastname comma:
            # last [suffix], title first middles[,] suffix [,suffix]
            #      parts[0],      parts[1],              parts[2:...]

            log.debug("post-comma pieces: %s", u(post_comma_pieces))

            # lastname part may have suffixes in it
            lex = shlex.shlex(parts[0], posix=True)
            lex.quotes = "/"
            lastname_pieces = self.parse_pieces(list(iter(lex.get_token, None)), 1)
            for piece in lastname_pieces:
                # the first one is always a last name, even if it looks like
                # a suffix
                if self.is_suffix(piece) and len(self.last_list) > 0:
                    self.suffix_list.append(piece)
                else:
                    self.last_list.append(piece)

            for i, piece in enumerate(post_comma_pieces):
                try:
                    nxt = post_comma_pieces[i + 1]
                except IndexError:
                    nxt = None

                if self.is_title(piece) \
                        and (nxt or len(post_comma_pieces) == 1) \
                        and not self.first:
                    self.title_list.append(piece)
                    continue
                if not self.first:
                    self.first_list.append(piece)
                    continue
                if self.is_suffix(piece):
                    self.suffix_list.append(piece)
                    continue
                self.middle_list.append(piece)
            try:
                if parts[2]:
                    self.suffix_list += parts[2:]
            except IndexError:
                pass

    if len(self) < 0:
        log.info("Unparsable: \"%s\" ", self.original)
    else:
        self.unparsable = False
    self.post_process()


HumanName.parse_full_name = parse_full_name


def parse_pieces(self, parts, additional_parts_count=0):
    """
    Split parts on spaces and remove commas, join on conjunctions and
    lastname prefixes. If parts have periods in the middle, try splitting
    on periods and check if the parts are titles or suffixes. If they are
    add to the constant so they will be found.

    :param list parts: name part strings from the comma split
    :param int additional_parts_count:

        if the comma format contains other parts, we need to know
        how many there are to decide if things should be considered a
        conjunction.
    :return: pieces split on spaces and joined on conjunctions
    :rtype: list
    """

    output = []
    for part in parts:
        if not isinstance(part, text_types):
            raise TypeError("Name parts must be strings. "
                            "Got {0}".format(type(part)))
        # Custom logic for familytree: doesn't split between /'s.
        # Example: /Tri Minh/ Doung -> first: "Tri Minh", last: "Doung"
        lex = shlex.shlex(part, posix=True)
        lex.quotes = "/"
        output += [x.strip(' ,') for x in iter(lex.get_token, None)]

    # If part contains periods, check if it's multiple titles or suffixes
    # together without spaces if so, add the new part with periods to the
    # constants so they get parsed correctly later
    for part in output:
        # if this part has a period not at the beginning or end
        if self.C.regexes.period_not_at_end.match(part):
            # split on periods, any of the split pieces titles or suffixes?
            # ("Lt.Gov.")
            period_chunks = part.split(".")
            titles = list(filter(self.is_title, period_chunks))
            suffixes = list(filter(self.is_suffix, period_chunks))

            # add the part to the constant so it will be found
            if len(list(titles)):
                self.C.titles.add(part)
                continue
            if len(list(suffixes)):
                self.C.suffix_not_acronyms.add(part)
                continue

    return self.join_on_conjunctions(output, additional_parts_count)


HumanName.parse_pieces = parse_pieces
