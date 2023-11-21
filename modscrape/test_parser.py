#
# Modscrape
# Unit Tests
# Parser
#

from parser import Parser, tokens_to_module
from typing import cast

import pytest

from lexer import lex
from module import Module, ModuleCode
from tok import Token, TokenType


# Utility function test
def test_tokens_to_module():
    for year in [None, Token(TokenType.NUMBER, "2")]:
        code, title = ModuleCode("SC1005"), "Digital Logic"
        module_mutually_exclusives = [ModuleCode("CZ1005")]
        module_pre_requisite_mods = [[ModuleCode(f"SC100{i}") for i in [1, 2]]]
        is_pass_fail = False

        actual = tokens_to_module(
            module_code=code,
            module_title=Token(TokenType.IDENTIFIER, title),
            module_au=Token(TokenType.AU, "3"),
            module_mutually_exclusives=module_mutually_exclusives,
            module_pre_requisite_year=year,
            module_pre_requisite_mods=module_pre_requisite_mods,
            module_pass_fail=is_pass_fail,
        )

        expected = Module(
            code=code,
            title=title,
            au=3,
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
        print(Parser(tokens).position)
        assert Parser(tokens).current_token() == expected


def test_parser_match(tokens: list[list[Token]]):
    parser = Parser(tokens)
    assert parser.match_no_move(TokenType.IDENTIFIER)
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
    cases = [
        ("SC1005", ModuleCode("SC1005")),
        ("MH1812(Corequisite)", ModuleCode("MH1812", is_corequisite=True)),
        (
            "CC0005(Miscellaneous information)",
            ModuleCode("CC0005", misc="Miscellaneous information"),
        ),
    ]
    for case, expected in cases:
        assert Parser(lex([case])).module_code() == expected


def test_parser_pass_fail():
    cases = [
        # input, return value, exception
        ("No match", False, None),
        ("Grade Type: Pass/Fail", True, None),
        ("Grade Type: Malformed", False, Exception),
    ]

    for text, expected, exception in cases:
        if exception is not None:
            with pytest.raises(exception):
                Parser(lex([text])).pass_fail()
            continue
        assert Parser(lex([text])).pass_fail() == expected
