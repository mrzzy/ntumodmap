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
from module import Module, ModuleCode
from tok import Token, TokenType


# Utility function tests
def test_tokens_to_module():
    for year in [None, Token(TokenType.NUMBER, "2")]:
        code, title = ModuleCode("SC1005"), "Digital Logic"
        module_mutually_exclusives = [ModuleCode("CZ1005")]
        module_pre_requisite_mods = [[ModuleCode(f"SC100{i}") for i in [1, 2]]]
        is_pass_fail = False

        actual = tokens_to_module(
            module_code=code,
            module_title=Token(TokenType.IDENTIFIER, title),
            # check that we handle parsing decimal AUs
            module_au=Token(TokenType.AU, "3.5"),
            module_mutually_exclusives=module_mutually_exclusives,
            module_pre_requisite_year=year,
            module_pre_requisite_mods=module_pre_requisite_mods,
            module_pass_fail=is_pass_fail,
        )

        expected = Module(
            code=code,
            title=title,
            au=3.5,
            mutually_exclusives=module_mutually_exclusives,
            needs_year=None if year is None else int(year.literal),
            needs_modules=module_pre_requisite_mods,
            rejects_courses=[],
            allowed_courses=[],
            rejects_modules=[],
            is_bde=False,
            is_pass_fail=is_pass_fail,
        )

        assert actual == expected


# Parser Tests
@dataclass
class ParseCase:
    """Parser test case.
    - text: The text to feed to the parser.
    - expected: If set, the expected parsing result to receive from the parser.
    - exception: If set, an exception of this type should be raised.
    """

    text: str
    expected: Optional[Any] = None
    exception: Optional[Type[Exception]] = None


def check_parser(cases: Iterable[ParseCase], method: Callable[[Parser], Any]):
    """Check that calling method on Parser passes the given ParseCases."""
    for case in cases:
        parser = Parser(lex([case.text]))
        if case.exception is not None:
            with pytest.raises(case.exception):
                method(parser)
            continue
        assert method(parser) == case.expected


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
            ParseCase("No match", False),
            ParseCase("Grade Type: Pass/Fail", True),
            ParseCase("Grade Type: Malformed", exception=Exception),
        ],
        method=Parser.pass_fail,
    )


def test_module_description():
    check_parser(
        cases=[
            ParseCase("No match", exception=Exception),
            ParseCase(
                "INTRODUCTION TO COMPUTATIONAL THINKING & PROGRAMMING 	3.0 AU",
                Token(
                    TokenType.IDENTIFIER,
                    "INTRODUCTION TO COMPUTATIONAL THINKING & PROGRAMMING",
                ),
            ),
        ],
        method=Parser.module_description,
    )


def test_au():
    check_parser(
        cases=[
            ParseCase("No number", exception=Exception),
            ParseCase("5 missing token", exception=Exception),
            ParseCase("3.0 AU", Token(TokenType.AU, "3.0"), None),
        ],
        method=Parser.au,
    )


def test_pre_requisite_year():
    check_parser(
        cases=[
            ParseCase("", None),
            # no comma after prerequisite
            ParseCase("Prerequisite", exception=Exception),
            ParseCase("Prerequisite:", None),
            ParseCase("Prerequisite: Year 3 standing", Token(TokenType.NUMBER, "3")),
            ParseCase(
                "Prerequisite: Study Year 4 standing", Token(TokenType.NUMBER, "4")
            ),
        ],
        method=Parser.pre_requisite_year,
    )


def test_pre_requisite_mods():
    check_parser(
        cases=[
            ParseCase("", []),
            # no comma after prerequisite
            ParseCase("Prerequisite", exception=Exception),
            ParseCase("Prerequisite:", []),
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


def test_mutally_exclusive():
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
