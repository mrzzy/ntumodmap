#
# Modscrape
# Unit Tests
# Parser
#

from dataclasses import dataclass
from parser import Parser, tokens_to_module
from typing import Any, Callable, Iterable, Optional, Type, cast

import pytest

from lexer import lex
from module import Course, Module, ModuleCode
from tok import KeyWords, Token, TokenType


# Utility function tests
def test_tokens_to_module():
    for year in [None, Token(TokenType.NUMBER, "2")]:
        code, title = ModuleCode("SC1005"), "Digital Logic"
        module_mutually_exclusives = [ModuleCode("CZ1005")]
        module_pre_requisite_mods = [[ModuleCode(f"SC100{i}") for i in [1, 2]]]
        module_pre_requisite_exclusives = Token(
            TokenType.IDENTIFIER, "for students who failed QET"
        )
        not_offered_as_bde = True
        not_offered_as_ue = False
        is_pass_fail = False
        module_description = Token(
            TokenType.IDENTIFIER,
            "This course aims to develop your ability to analyse and design digital circuits.",
        )

        actual = tokens_to_module(
            module_code=code,
            module_title=Token(TokenType.IDENTIFIER, title),
            # check that we handle parsing decimal AUs
            module_au=Token(TokenType.AU, "3.5"),
            module_mutually_exclusives=module_mutually_exclusives,
            module_pre_requisite_year=year,
            module_pre_requisite_mods=module_pre_requisite_mods,
            module_pre_requisite_exclusives=module_pre_requisite_exclusives,
            module_reject_courses=[],
            module_reject_courses_with=[],
            module_unavailable_as_pe=[],
            module_not_offered_as_bde=not_offered_as_bde,
            module_not_offered_as_ue=not_offered_as_ue,
            module_pass_fail=is_pass_fail,
            module_description=module_description,
        )

        expected = Module(
            code=code,
            title=title,
            au=3.5,
            mutually_exclusives=module_mutually_exclusives,
            needs_year=None if year is None else int(year.literal),
            needs_modules=module_pre_requisite_mods,
            needs_exclusives=module_pre_requisite_exclusives.literal,
            rejects_courses=[],
            rejects_courses_with=[],
            unavailable_as_pe=[],
            allowed_courses=[],
            rejects_modules=[],
            not_offered_as_bde=not_offered_as_bde,
            not_offered_as_ue=not_offered_as_ue,
            is_pass_fail=is_pass_fail,
            description=module_description.literal,
        )

        assert actual == expected


# Parser Tests
@dataclass
class ParseCase:
    """Parser test case.
    - text: The text to feed to the parser.
    - expected: If set, the expected parsing result to receive from the parser.
    - exception: If set, an exception of this type should be raised.
    - position: If set, how many tokens the parser should shift its inputs.
        By default this is set to the number of tokens in the text input or 0
        if exception is set.
    """

    text: str
    expected: Optional[Any] = None
    exception: Optional[Type[Exception]] = None
    position: Optional[int] = None

    def __post_init__(self):
        # called after __init__()
        self.tokens = lex([self.text])
        if self.position is not None:
            self.n_shifts = self.position
        elif self.exception is not None:
            self.n_shifts = 0
        else:
            self.n_shifts = len(self.tokens[0])


def check_parser(cases: Iterable[ParseCase], method: Callable[[Parser], Any]):
    """Check that calling method on Parser passes the given ParseCases."""
    for case in cases:
        parser = Parser(case.tokens)
        # check parser functionality
        if case.exception is not None:
            with pytest.raises(case.exception):
                method(parser)
        else:
            assert method(parser) == case.expected
        # check parser position
        assert parser.position == case.n_shifts


@pytest.fixture
def tokens() -> list[list[Token]]:
    return lex(["The quick brown fox jumped over the ledge,", "and died."])


def test_parser_current_token(tokens: list[list[Token]]):
    # check out of bounds handling
    for tokens, expected in [
        (cast(list[list[Token]], []), None),
        (cast(list[list[Token]], [[]]), None),
        (tokens, tokens[0][0]),
    ]:
        assert Parser(tokens).current_token() == expected


def test_parser_match(tokens: list[list[Token]]):
    parser = Parser(tokens)
    assert parser.match_no_move(TokenType.IDENTIFIER)
    assert parser.position == 0
    assert parser.match(TokenType.IDENTIFIER)
    assert parser.position == 1
    assert parser.match_literal(TokenType.IDENTIFIER, "quick")
    assert parser.position == 2
    assert parser.match_identifier("brown")
    assert parser.position == 3
    assert parser.match_consecutive_identifiers(["fox", "jumped"])
    assert parser.position == 5
    assert parser.match_consecutive([TokenType.IDENTIFIER for _ in range(2)])
    assert parser.position == 7
    assert parser.match_consecutive_literals(
        [TokenType.IDENTIFIER, TokenType.COMMA],
        ["ledge", ","],
    )
    assert parser.position == len(tokens[0])


def test_parser_match_mismatch_no_move(tokens: list[list[Token]]):
    # check that does not move upon matching does match wrong token type
    parser = Parser(tokens)
    assert not parser.match_no_move(TokenType.NUMBER)
    assert parser.position == 0
    assert not parser.match(TokenType.NUMBER)
    assert parser.position == 0
    assert not parser.match_multi([TokenType.IDENTIFIER, TokenType.NUMBER])
    assert parser.position == 0
    assert not parser.match_consecutive([TokenType.IDENTIFIER, TokenType.NUMBER])
    assert parser.position == 0
    assert not parser.match_literal(TokenType.IDENTIFIER, "mismatch")
    assert parser.position == 0
    assert not parser.match_identifier("mismatch")
    assert parser.position == 0
    assert not parser.match_consecutive_identifiers(["The", "mismatch"])
    assert parser.position == 0


def test_parser_match_au():
    # check parser does not match if no period is present
    parser = Parser(lex(["1"]))
    assert not parser.match_au()
    assert parser.position == 0

    # check parser matches au
    for case in ["3.0", ".0", "8.5"]:
        parser = Parser(lex([case]))
        assert parser.match_au()
        assert parser.position == len(case)


def test_parser_consume(tokens: list[list[Token]]):
    # wrong token type
    parser = Parser(tokens)
    with pytest.raises(Exception):
        parser.consume(TokenType.PREREQ, "wrong token type")

    # consume single
    assert parser.consume(TokenType.IDENTIFIER, "no identifier") == tokens[0][0]
    assert parser.position == 1

    # consume multi
    parser.position = len(tokens[0]) - 2
    assert (
        parser.consume_multi(
            [TokenType.IDENTIFIER, TokenType.COMMA], "no identifier followed by comma"
        )
        == tokens[0][-1]
    )
    assert parser.position == len(tokens[0])

    # exhausted tokens
    with pytest.raises(Exception):
        parser.consume(TokenType.IDENTIFIER, "end of string")
    with pytest.raises(Exception):
        parser.consume_multi([TokenType.IDENTIFIER], "end of string")


def test_parser_mischellaneous():
    check_parser(
        cases=[
            ParseCase("No match", exception=Exception),
            ParseCase("No match)", exception=Exception),
            ParseCase("(No match", exception=Exception),
            ParseCase("()", ""),
            ParseCase("(match this) not this", "match this", position=4),
            # check non identifier tokens are considered miscellaneous if
            # surrounded by parenthesis
            ParseCase("(Grade this) not this", "Grade this", position=4),
            ParseCase("(Type this) not this", "Type this", position=4),
        ],
        method=Parser.miscellaneous,
    )


def test_parser_module_code():
    check_parser(
        cases=[
            ParseCase("SC1005", ModuleCode("SC1005")),
            ParseCase("MH1812(Corequisite)", ModuleCode("MH1812", is_corequisite=True)),
            ParseCase(
                "CC0005(Miscellaneous information)",
                ModuleCode("CC0005", misc="Miscellaneous information"),
            ),
            ParseCase("::SC1005", exception=Exception),
        ],
        method=Parser.module_code,
    )


def test_parser_pass_fail():
    check_parser(
        cases=[
            # input, return value, exception
            ParseCase("No match", False, position=0),
            ParseCase("Grade Type: Pass/Fail", True),
            ParseCase("Grade Type: Malformed", exception=Exception),
        ],
        method=Parser.pass_fail,
    )


def test_parser_module_title():
    check_parser(
        cases=[
            ParseCase("No match", exception=Exception),
            ParseCase(
                "INTRODUCTION TO COMPUTATIONAL THINKING & PROGRAMMING 	3.0 AU",
                Token(
                    TokenType.IDENTIFIER,
                    "INTRODUCTION TO COMPUTATIONAL THINKING & PROGRAMMING",
                ),
                position=6,
            ),
            ParseCase(
                "INTRODUCTION TO ACADEMIC COMMUNICATION 	.0 AU",
                Token(
                    TokenType.IDENTIFIER,
                    "INTRODUCTION TO ACADEMIC COMMUNICATION",
                ),
                position=4,
            ),
            ParseCase(
                "MATHEMATICS 1 	3.0 AU",
                Token(TokenType.IDENTIFIER, "MATHEMATICS 1"),
                position=2,
            ),
        ],
        method=Parser.module_title,
    )


def test_parser_au():
    check_parser(
        cases=[
            ParseCase("No number", exception=Exception),
            ParseCase("5 missing token", exception=Exception),
            ParseCase("3.0 AU", Token(TokenType.AU, "3.0")),
            ParseCase(".0 AU", Token(TokenType.AU, ".0")),
            ParseCase("3.5 ADM", Token(TokenType.AU, "3.5")),
            ParseCase("8.0 BIE(CBE)", Token(TokenType.AU, "8.0")),
        ],
        method=Parser.au,
    )


def test_parser_pre_requisite_year():
    check_parser(
        cases=[
            ParseCase("", None),
            # no comma after prerequisite
            ParseCase("Prerequisite", exception=Exception),
            ParseCase("Prerequisite:", None, position=0),
            ParseCase("Prerequisite: Year 3 standing", Token(TokenType.NUMBER, "3")),
            ParseCase(
                "Prerequisite: Study Year 4 standing", Token(TokenType.NUMBER, "4")
            ),
        ],
        method=Parser.pre_requisite_year,
    )


def test_parser_pre_requisite_mods():
    check_parser(
        cases=[
            ParseCase("", []),
            # no comma after prerequisite
            ParseCase("Prerequisite", exception=Exception),
            ParseCase("Prerequisite:", [], position=0),
            ParseCase(
                text="Prerequisite: CZ1007 & CZ2001(Corequisite)"
                " OR CE1007 & CE2001(Corequisite)"
                " OR CE1007 & CZ2001(Corequisite)"
                " OR CE2001(Corequisite) & CZ1007",
                expected=[
                    [ModuleCode("CZ1007"), ModuleCode("CZ2001", is_corequisite=True)],
                    [ModuleCode("CE1007"), ModuleCode("CE2001", is_corequisite=True)],
                    [ModuleCode("CE1007"), ModuleCode("CZ2001", is_corequisite=True)],
                    [ModuleCode("CE2001", is_corequisite=True), ModuleCode("CZ1007")],
                ],
            ),
        ],
        method=Parser.pre_requisite_mods,
    )


def test_parser_pre_requisite_exclusives():
    check_parser(
        cases=[
            ParseCase("", None),
            ParseCase("Prerequisite", exception=Exception),
            ParseCase("Prerequisite:", Token(TokenType.IDENTIFIER, "")),
            ParseCase(
                text="Prerequisite: Only for Premier Scholars Programme students",
                expected=Token(
                    TokenType.IDENTIFIER,
                    "Only for Premier Scholars Programme students",
                ),
            ),
        ],
        method=Parser.pre_requisite_exclusives,
    )


def test_parser_mutally_exclusive():
    check_parser(
        cases=[
            ParseCase("", []),
            # no comma after "Mutually exclusive with"
            ParseCase("Mutually exclusive with", exception=Exception),
            ParseCase("Mutually exclusive with:", []),
            ParseCase(
                text="Mutually exclusive with: CE4031, SC3020",
                expected=[ModuleCode("CE4031"), ModuleCode("SC3020")],
            ),
        ],
        method=Parser.mutually_exclusive,
    )


def test_parser_not_available_to_programme():
    check_parser(
        cases=[
            ParseCase("", []),
            ParseCase("Not available to Programme", exception=Exception),
            ParseCase("Not available to Programme:", []),
            ParseCase(
                text="Not available to Programme: CE",
                expected=[Course("CE", None, None, None, None)],
            ),
            ParseCase(
                text="Not available to Programme: REP(CSC)",
                expected=[Course("REP", None, None, None, "CSC")],
            ),
            ParseCase(
                text="Not available to Programme: REP(CSC), REP(CE)",
                expected=[
                    Course("REP", None, None, None, "CSC"),
                    Course("REP", None, None, None, "CE"),
                ],
            ),
            ParseCase(
                text="Not available to Programme: EEE(Direct Entry)",
                expected=[
                    Course("EEE", True, None, None, None),
                ],
            ),
            ParseCase(
                text="Not available to Programme: EEE(2018-onwards)(Non Direct Entry)",
                expected=[
                    Course("EEE", False, 2018, 9999, None),
                ],
            ),
            ParseCase(
                text="Not available to Programme: EEE(2018-onwards)(Non Direct Entry), IEM(2019-onwards)(Direct Entry), MEEC(RMS)(2020-onwards)(Direct Entry)",
                expected=[
                    Course("EEE", False, 2018, 9999, None),
                    Course("IEM", True, 2019, 9999, None),
                    Course("MEEC", True, 2020, 9999, "RMS"),
                ],
            ),
        ],
        method=Parser.not_available_to_programme,
    )


def test_parser_not_available_to_programme_with():
    check_parser(
        cases=[
            ParseCase("", []),
            ParseCase("Not available to all Programme with", exception=Exception),
            ParseCase("Not available to all Programme with:", []),
            ParseCase(
                text="Not available to all Programme with: (Admyr 2021-onwards)",
                expected=[Course(KeyWords.ADMYR, None, 2021, 9999, None)],
            ),
            ParseCase(
                text="Not available to all Programme with: (Admyr 2011-2019), (Admyr 2021-onwards)",
                expected=[
                    Course(KeyWords.ADMYR, None, 2011, 2019, None),
                    Course(KeyWords.ADMYR, None, 2021, 9999, None),
                ],
            ),
        ],
        method=Parser.not_available_to_programme_with,
    )


def test_parser_not_offered_as_bde():
    check_parser(
        cases=[
            ParseCase("", False),
            ParseCase("Not offered as Broadening and Deepening Elective", True),
        ],
        method=Parser.not_offered_as_bde,
    )


def test_parser_not_offered_as_ue():
    check_parser(
        cases=[
            ParseCase("", False),
            ParseCase("Not offered as Unrestricted Elective", True),
        ],
        method=Parser.not_offered_as_ue,
    )
