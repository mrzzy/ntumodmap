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

def lex(lines: list[str]) -> list[Token]:
    tokens: list[Token] = []
    current: int = 0
    for line in lines:
        while current < len(line):
            character = line[current]
            current += 1
            if (character == ' ' or
                character == '\t' or
                character == '\n'):
                continue
            elif character == TokenType.DOT:
                tokens.append(Token(TokenType.DOT, "."))
            elif character == TokenType.COMMA:
                tokens.append(Token(TokenType.COMMA, ","))
            elif character == TokenType.COLON:
                tokens.append(Token(TokenType.COLON, ":"))
            elif character == TokenType.SEMICOLON:
                tokens.append(Token(TokenType.SEMICOLON, ";"))
            elif character == TokenType.LPAREN:
                tokens.append(Token(TokenType.LPAREN, "("))
            elif character == TokenType.RPAREN:
                tokens.append(Token(TokenType.RPAREN, ")"))
            elif character == TokenType.LBRACE:
                tokens.append(Token(TokenType.LBRACE, "{"))
            elif character == TokenType.RBRACE:
                tokens.append(Token(TokenType.RBRACE, "}"))
            elif character == TokenType.LBRACKET:
                tokens.append(Token(TokenType.LBRACKET, "["))
            elif character == TokenType.RBRACKET:
                tokens.append(Token(TokenType.RBRACKET, "]"))
            elif character.isalpha():
                # check if its a keyword
                extend = current
                while extend < len(line) and line[extend].isalpha():
                    extend += 1
                identifier = line[current-1:extend]
                if is_keyword(identifier):
                    tokens.append(Token(keywords[identifier], identifier))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier))
                current = extend
    return tokens



