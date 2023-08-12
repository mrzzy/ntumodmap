from enum import Enum

class TokenType(Enum):
    # Mod cred
    AU = "AU"

    # Grade Type
    GRADE_TYPE = "Grade Type"
    PASS = "Pass"
    FAIL = "Fail"

    # Prereq/Coreq
    PREREQ = "Prerequisite"
    COREQ = "Corequisite"
    # Some prereqs are listed as X OR Y OR Z
    OR = "OR"

    MUTUALLY_EXCLUSIVE = "Mutually exclusive with"
    NOT_AVAIL_TO_PROG = "Not available to Programme"
    NOT_AVAIL_TO_PROG_WITH = "Not available to all Programme with"
    NOT_AVAIL_AS_PE_TO_PROG = "Not available as PE to Programme"
    NOT_OFFERED_AS_UE = "Not offered as Unrestricted Elective"
    NOT_OFFERED_AS_BDE = "Not offered as Broadening and Deepening Elective"

    DOT       = "."
    COMMA     = ","
    COLON     = ":"
    SEMICOLON = ";"
    LPAREN    = "("
    RPAREN    = ")"
    LBRACE    = "{"
    RBRACE    = "}"
    LBRACKET  = "["
    RBRACKET  = "]"
    DASH      = "-"
    AMP       = "&"

    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"

class Token:
    def __init__(self, token_type: TokenType, literal: str):
        self.token_type = token_type
        self.literal = literal
    def __repr__(self):
        return f"({self.token_type}, {self.literal})"
