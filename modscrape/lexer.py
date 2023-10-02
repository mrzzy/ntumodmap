from tok import Token, TokenType

keywords: dict[str, TokenType] = {
    "AU": TokenType.AU,
    "Grade Type": TokenType.GRADE_TYPE,
    "Pass": TokenType.PASS,
    "Fail": TokenType.FAIL,
    "Prerequisite": TokenType.PREREQ,
    "Corequisite": TokenType.COREQ,
    "OR": TokenType.OR,
    "Mutually exclusive with": TokenType.MUTUALLY_EXCLUSIVE,
    "Not available to Programme": TokenType.NOT_AVAIL_TO_PROG,
    "Not available to all Programme with": TokenType.NOT_AVAIL_TO_PROG_WITH,
    "Not available as PE to Programme": TokenType.NOT_AVAIL_AS_PE_TO_PROG,
    "Not offered as Unrestricted Elective": TokenType.NOT_OFFERED_AS_UE,
    "Not offered as Broadening and Deepening Elective": TokenType.NOT_OFFERED_AS_BDE
}

def is_keyword(text: str) -> bool:
    if keywords.get(text) != None:
        return True
    return False

def lex(lines: list[str]) -> list[list[Token]]:
    tokens: list[list[Token]] = []
    current: int = 0
    for line in lines:
        sub_tokens: list[Token] = []
        while current < len(line):
            character = line[current]
            current += 1
            if (character == ' ' or
                character == '\t' or
                character == '\n'):
                continue
            elif character == ".":
                sub_tokens.append(Token(TokenType.DOT, "."))
            elif character == ",":
                sub_tokens.append(Token(TokenType.COMMA, ","))
            elif character == ":":
                sub_tokens.append(Token(TokenType.COLON, ":"))
            elif character == ";":
                sub_tokens.append(Token(TokenType.SEMICOLON, ";"))
            elif character == "(":
                sub_tokens.append(Token(TokenType.LPAREN, "("))
            elif character == ")":
                sub_tokens.append(Token(TokenType.RPAREN, ")"))
            elif character == "{":
                sub_tokens.append(Token(TokenType.LBRACE, "{"))
            elif character == "}":
                sub_tokens.append(Token(TokenType.RBRACE, "}"))
            elif character == "[":
                sub_tokens.append(Token(TokenType.LBRACKET, "["))
            elif character == "]":
                sub_tokens.append(Token(TokenType.RBRACKET, "]"))
            elif character == "-":
                sub_tokens.append(Token(TokenType.DASH, "-"))
            elif character == "&":
                sub_tokens.append(Token(TokenType.AMP, "&"))
            elif character == "'":
                sub_tokens.append(Token(TokenType.SINGLE_QUOTE, "'"))
            elif character == '"':
                sub_tokens.append(Token(TokenType.DOUBLE_QUOTE, '"'))
            elif character == "/":
                sub_tokens.append(Token(TokenType.SLASH, "/"))
            elif character == "`":
                sub_tokens.append(Token(TokenType.BACKTICK, "`"))
            elif character == "?":
                sub_tokens.append(Token(TokenType.QUESTION_MARK, "?"))
            elif character.isalnum():
                extend = current
                while extend < len(line) and line[extend].isalnum():
                    extend += 1
                identifier = line[current-1:extend]
                # check if its a keyword, otherwise its an identifier
                if is_keyword(identifier):
                    sub_tokens.append(Token(keywords[identifier], identifier))
                elif identifier.isdigit():
                    sub_tokens.append(Token(TokenType.NUMBER, identifier))
                else:
                    if (len(identifier) == 6 and
                        identifier[0].isalpha() and
                        identifier[1].isalpha() and
                        identifier[2].isdigit() and
                        identifier[3].isdigit() and
                        identifier[4].isdigit() and
                        identifier[5].isdigit()):
                        sub_tokens.append(Token(TokenType.MODULE_CODE, identifier))
                    else:
                        sub_tokens.append(Token(TokenType.IDENTIFIER, identifier))
                current = extend
            else:
                print("Currently not supported: ", character, ord(character))
        tokens.append(sub_tokens)
        current = 0
    return tokens



