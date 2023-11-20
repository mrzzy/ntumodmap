#
# Modscrape
# Unit Tests
# Parser
#

from parser import Parser, tokens_to_module

from lexer import lex
from module import Module, ModuleCode
from tok import Token, TokenType


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


def test_parser_current_token():
    # check out of bounds handling
    token = Token(TokenType.IDENTIFIER, "Something")
    for tokens, expected in [
        ([], None),
        ([[]], None),
        ([[token]], token),
    ]:
        assert Parser(tokens).current_token() == expected


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
