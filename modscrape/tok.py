#
# Token
# Literal string representations of the Token enum
#

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    # Mod cred
    AU = "AU"

    # Grade Type
    GRADE = "Grade"
    TYPE = "Type"
    PASS = "Pass"
    FAIL = "Fail"

    # Prereq/Coreq
    PREREQ = "Prerequisite"
    COREQ = "Corequisite"
    # Some prereqs are listed as X OR Y OR Z
    OR = "OR"
    AND = "&"
    AND_TEXT = "and"

    MUTUALLY = "Mutually"
    EXCLUSIVE = "exclusive"
    WITH = "with"
    NOT = "Not"
    AVAIL = "available"
    TO = "to"
    ALL = "all"
    PROGRAMME = "Programme"
    AS = "as"
    PE = "PE"
    OFFERED = "offered"
    UNRESTRICTED = "Unrestricted"
    ELECTIVE = "Elective"
    BROADENING = "Broadening"
    DEEPENING = "Deepening"
    STANDING = "standing"

    MUTUALLY_EXCLUSIVE = "Mutually exclusive with"
    NOT_AVAIL_TO_PROG = "Not available to Programme"
    NOT_AVAIL_TO_PROG_WITH = "Not available to all Programme with"
    NOT_AVAIL_AS_PE_TO_PROG = "Not available as PE to Programme"
    NOT_OFFERED_AS_UE = "Not offered as Unrestricted Elective"
    NOT_OFFERED_AS_BDE = "Not offered as Broadening and Deepening Elective"

    DOT = "."
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    DASH = "-"
    AMP = "&"
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    PLUS = "+"
    SLASH = "/"
    BACKTICK = "`"
    QUESTION_MARK = "?"

    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"

    # This specifically refers to identifiers that starts with XX1234
    MODULE_CODE = "MODULE_CODE"


@dataclass
class Token:
    token_type: TokenType
    literal: str

    def __repr__(self):
        return f"({self.token_type}, {self.literal})"


def flatten_tokens(token_type: TokenType, tokens: list[Token], interval=" ") -> Token:
    return Token(token_type, interval.join([token.literal for token in tokens]))
