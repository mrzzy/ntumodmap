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

class Token:
    token_type: TokenType
    literal: str

def lex(lines: list[str]):
    print(lines)
