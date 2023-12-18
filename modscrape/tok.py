#
# Token
# Literal string representations of the Token enum
#

from dataclasses import dataclass
from enum import Enum

# These are textual keywords - we don't want to manually type in the keywords for identifiers
# we just match them to these:
# e.g. Mutually Exclusive => match_consecutive_identifiers([KeyWords.MUTUALLY, KeyWords.EXCLUSIVE])
class KeyWords:
    AVAIL = "available"
    TO = "to"
    ALL = "all"
    PROGRAMME = "Programme"
    AS = "as"
    PE = "PE"
    AND = "and"

    MUTUALLY = "Mutually"
    EXCLUSIVE = "exclusive"
    WITH = "with"
    NOT = "Not"
    OFFERED = "offered"

    UNRESTRICTED = "Unrestricted"
    ELECTIVE = "Elective"
    BROADENING = "Broadening"
    DEEPENING = "Deepening"

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
    STANDING = "standing"

    # Some prereqs are listed as X OR Y OR Z
    OR = "OR"
    AND = "&"

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
