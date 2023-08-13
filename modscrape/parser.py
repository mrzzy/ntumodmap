import sys
from tok import Token, TokenType
from typing import Optional, Callable
from module import Module

def contextual(func: Callable[[], Optional[Module]], parser: 'Parser') -> Optional[Module]:
    # Resets position if `func` returns None.
    def contextual_wrapper(parser: Parser) -> Optional[Module]:
        # Gets the starting position
        begin = parser.position
        # Try to run the function
        res = func()
        # If function parses Nothing => returns None
        if res is None:
            # Sets the position back to where it started
            parser.set_position(begin)
            return
        return res
    return contextual_wrapper(parser)

class Parser():
    def __init__(self, tokens: list[list[Token]]):
        self.tokens = tokens

        # This indicates which of the inner list of `tokens`
        # we are currently iterating over
        self.paragraph = 0
        # This indicates which token within the paragraph
        self.position = 0

    def set_position(self, position):
        self.position = position

    def current_token(self) -> Optional[Token]:
        return self.tokens[self.paragraph][self.position]

    def previous_token(self) -> Optional[Token]:
        """
        # If the previous token is the previous paragraph,
        # this will have to reflect that
        if self.position == 0 and self.paragraph != 0 :
            # Return the last element in the previous paragraph
            return self.tokens[self.paragraph-1][-1]
        if self.position > 0:
            return self.tokens[self.paragraph][self.position-1]
        # This case will hit for the case being at the
        # start of the parsing phase
        """
        if self.position > 0:
            return self.tokens[self.paragraph][self.position-1]
        return None

    def move(self):
        """
        # In the case that there is a token to be moved
        if self.position != len(self.tokens[self.paragraph])-1:
            self.position += 1
        else: # In the case that there is no more tokens in the current paragraph
            self.paragraph += 1
            self.position = 0
        """
        self.position += 1

    # Takes in a TokenType, if the current token is of the same TokenType
    # it will move the position up
    def match(self, token_type: TokenType) -> bool:
        current_token = self.current_token()
        if current_token == None: return False
        if current_token.token_type == token_type:
            self.move()
            return True
        # All other cases are false
        return False

    # Takes in a list of [TokenType], if the current token is of the same TokenType
    # it will move the position up
    def match_multi(self, token_types: list[TokenType]) -> bool:
        current_token = self.current_token()
        if current_token == None: return False
        for token_type in token_types:
            if current_token.token_type == token_type:
                self.move()
                return True
        return False

    def consume(self, token_type: TokenType, error: str) -> Optional[Token]:
        try_match = self.match(token_type)
        # If it failed to match: return an error
        if not try_match:
            current_token = self.current_token()
            if current_token is not None:
                print(error, file=sys.stderr)
                print(f"Error: expected {token_type} but received {current_token.token_type}",
                      file=sys.stderr)
                return None
        return self.previous_token()

    def consume_multi(self,
                      token_types: list[TokenType],
                      error: str) -> Optional[Token]:
        try_match = self.match_multi(token_types)
        if not try_match:
            current_token = self.current_token()
            if current_token is not None:
                print(error, file=sys.stderr)
                print(f"Error: expected {token_types} but received {current_token.token_type}",
                      file=sys.stderr)
                return None
        return self.previous_token()

    def parse_module(self) -> Optional[Module]:
        identifier: Optional[Token] = self.consume(TokenType.IDENTIFIER, "Expected an identifier to start off a module")
        if identifier is not None:
            print(identifier)
        sys.exit(0)
        return None

    def parse(self) -> list[Module]:
        modules: list[Module] = []
        for _ in self.tokens:
            module = self.parse_module()
            if module is not None:
                modules.append(module)
                # Reset the indices and move on to the next module
                self.paragraph += 1
                self.position = 0
        return modules

def parse(tokens: list[list[Token]]) -> list[Module]:
    parser = Parser(tokens)
    return parser.parse()
