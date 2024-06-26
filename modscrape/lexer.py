#
# Lexer
# Turns the strings into tokens to be parsed
#

from typing import Iterable

from tok import Token, TokenType

token_types: dict[str, TokenType] = {
    "AU": TokenType.AU,
    "Grade": TokenType.GRADE,
    "Type": TokenType.TYPE,
    "Pass": TokenType.PASS,
    "Fail": TokenType.FAIL,
    "Prerequisite": TokenType.PREREQ,
    "Corequisite": TokenType.COREQ,
    "OR": TokenType.OR,
    "standing": TokenType.STANDING,
}


def lex(lines: Iterable[str]) -> list[list[Token]]:
    tokens: list[list[Token]] = []
    current: int = 0
    for line in lines:
        sub_tokens: list[Token] = []
        while current < len(line):
            character = line[current]
            current += 1
            if character == " " or character == "\t" or character == "\n":
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
            elif character == "+":
                sub_tokens.append(Token(TokenType.PLUS, "+"))
            elif character == "`":
                sub_tokens.append(Token(TokenType.BACKTICK, "`"))
            elif character == "?":
                sub_tokens.append(Token(TokenType.QUESTION_MARK, "?"))
            elif character.isalnum():
                extend = current
                while extend < len(line) and line[extend].isalnum():
                    extend += 1
                identifier = line[current - 1 : extend]
                # check if its a token type, otherwise its an identifier
                if identifier in token_types:
                    sub_tokens.append(Token(token_types[identifier], identifier))
                elif identifier.isdigit():
                    sub_tokens.append(Token(TokenType.NUMBER, identifier))
                else:
                    if (
                        len(identifier) == 6
                        and identifier[0].isalpha()
                        and identifier[1].isalpha()
                        and identifier[2].isdigit()
                        and identifier[3].isdigit()
                        and identifier[4].isdigit()
                        and identifier[5].isdigit()
                    ):
                        sub_tokens.append(Token(TokenType.MODULE_CODE, identifier))
                    else:
                        sub_tokens.append(Token(TokenType.IDENTIFIER, identifier))
                current = extend
            else:
                print("Currently not supported: ", character, ord(character))
        tokens.append(sub_tokens)
        current = 0
    return tokens
