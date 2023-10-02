import sys
from tok import Token, TokenType, flatten_tokens
from typing import Optional, Callable, TypeVar
from module import Module

# I note that this may be bad practice but I dont see any other way to
# unwrap an optional
# This makes it so that unwrap is generic
T = TypeVar("T")


def unwrap(arg: Optional[T]) -> T:
    assert arg is not None
    return arg


def contextual(
    func: Callable[[], Optional[Module]], parser: "Parser"
) -> Optional[Module]:
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


def tokens_to_module(
    module_code: Token,
    module_title: Token,
    module_au: Token,
) -> Module:
    code = module_code.literal
    title = module_title.literal
    au = float(module_au.literal)

    assert type(code) == str
    assert type(title) == str
    assert type(au) == float

    return Module(code, title, au)


class Parser:
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
            return self.tokens[self.paragraph][self.position - 1]
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

    # Takes in a TokenType, checks if the current token is of the same TokenType
    def match_no_move(self, token_type: TokenType) -> bool:
        current_token = self.current_token()
        if current_token == None:
            return False
        if current_token.token_type == token_type:
            return True
        # All other cases are false
        return False

    # Takes in a TokenType, if the current token is of the same TokenType
    # it will move the position up
    def match(self, token_type: TokenType) -> bool:
        current_token = self.current_token()
        if current_token == None:
            return False
        if current_token.token_type == token_type:
            self.move()
            return True
        # All other cases are false
        return False

    # Takes in a list of [TokenType], if the current token is of the same TokenType
    # it will move the position up
    def match_multi(self, token_types: list[TokenType]) -> bool:
        current_token = self.current_token()
        if current_token == None:
            return False
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
                print(
                    f"Error: expected {token_type} but received {current_token.token_type}",
                    file=sys.stderr,
                )
                return None
        return self.previous_token()

    def consume_multi(
        self, token_types: list[TokenType], error: str
    ) -> Optional[Token]:
        try_match = self.match_multi(token_types)
        if not try_match:
            current_token = self.current_token()
            if current_token is not None:
                print(error, file=sys.stderr)
                print(
                    f"Error: expected {token_types} but received {current_token.token_type}",
                    file=sys.stderr,
                )
                return None
        return self.previous_token()

    def au(self) -> Optional[Token]:
        number: Optional[Token] = self.consume(
            TokenType.NUMBER, "Expected a number to indicate AUs"
        )
        if number is None:
            return None

        aus = [number]
        while not self.match(TokenType.AU):
            token = self.current_token()
            self.move()
            aus.append(token)
        aus = flatten_tokens(TokenType.AU, aus, interval="")

        return aus

    def module(self) -> Optional[Module]:
        # e.g. CB1131, SC1005, SC1007
        module_code: Optional[Token] = self.consume(
            TokenType.MODULE_CODE, "Expected an module code to start off a module"
        )
        if module_code is None:
            return None

        # Parse module name until the numeric AU
        # e.g. Introduction to Computational Thinking
        module_description = []
        while not self.match_no_move(TokenType.NUMBER):
            token = self.current_token()
            self.move()
            module_description.append(token)
        module_description = flatten_tokens(TokenType.IDENTIFIER, module_description)

        # Parse numeric AU
        module_au = self.au()

        module = tokens_to_module(module_code, module_description, module_au)
        # sys.exit(0)
        return module

    def parse(self) -> list[Module]:
        modules: list[Module] = []
        for _ in self.tokens:
            module = self.module()
            if module is not None:
                modules.append(module)
                # Reset the indices and move on to the next module
                self.paragraph += 1
                self.position = 0
        return modules


def parse(tokens: list[list[Token]]) -> list[Module]:
    parser = Parser(tokens)
    return parser.parse()