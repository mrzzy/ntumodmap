#
# Parser
# Parses a list[list[Token]] into list[Module]
# The information the modules have in them should be
# further analyzed and turned into a graph
# This will just produce a flat structure of [Modude]
#

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
    module_mutually_exclusives: Optional[list[Token]],
    module_pre_requisite_year: Optional[Token],
    module_pre_requisite_mods: list[list[Token]],
) -> Module:
    code = module_code.literal
    title = module_title.literal
    au = float(module_au.literal)
    if module_mutually_exclusives is None:
        mutually_exclusives = []
    else:
        mutually_exclusives = [tok.literal for tok in module_mutually_exclusives]

    # To be filled in:
    rejects_modules = []
    rejects_courses = []
    allowed_courses = []
    is_bde = False

    assert type(code) == str
    assert type(title) == str
    assert type(au) == float

    return Module(
        code,
        title,
        au,
        mutually_exclusives,
        module_pre_requisite_year,
        module_pre_requisite_mods,
        rejects_modules,
        rejects_courses,
        allowed_courses,
        is_bde,
    )


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

    def match_identifier(self, identifier_literal: str) -> bool:
        current_token = self.current_token()
        if current_token == None:
            return False
        if current_token.token_type != TokenType.IDENTIFIER:
            return False
        if current_token.literal == identifier_literal:
            self.move()
            return True
        return False

    def match_consecutive(self, token_types: list[TokenType]) -> bool:
        while len(token_types) > 0:
            if not self.match(token_types[0]):
                return False
            token_types.pop(0)
        return True

    def match_consecutive_literals(
        self, token_types: list[TokenType], token_literals: list[str]
    ) -> bool:
        assert len(token_types) == len(token_literals)
        while len(token_types) > 0:
            token = self.current_token()
            if not self.match(token_types[0]):
                return False
            if token.literal != token_literals[0]:
                return False
            token_types.pop(0)
        return True

    def match_consecutive_identifiers(self, token_literals: list[str]) -> bool:
        while len(token_literals) > 0:
            if not self.match_identifier(token_literals[0]):
                return False
            token_literals.pop(0)
        return True

    def consume(self, token_type: TokenType, error: str) -> Optional[Token]:
        try_match = self.match(token_type)
        # If it failed to match: return an error
        if not try_match:
            current_token = self.current_token()
            if current_token is not None:
                raise Exception(
                    f"Error: expected {token_type} but received {current_token.token_type}",
                )
        return self.previous_token()

    def consume_multi(
        self, token_types: list[TokenType], error: str
    ) -> Optional[Token]:
        try_match = self.match_multi(token_types)
        if not try_match:
            current_token = self.current_token()
            if current_token is not None:
                raise Exception(
                    f"Error: expected {token_type} but received {current_token.token_type}",
                )
                return None
        return self.previous_token()

    def module_code(self) -> Optional[Token]:
        # e.g. CB1131, SC1005, SC1007
        module_code: Optional[Token] = self.consume(
            TokenType.MODULE_CODE, "Expected an module code to start off a module"
        )
        # If the module code is MH1812(Corequisite), this will catch that and parse it in
        if self.match_consecutive(
            [TokenType.LPAREN, TokenType.COREQ, TokenType.RPAREN]
        ):
            module_code.literal += (
                str(TokenType.LPAREN) + str(TokenType.COREQ) + str(TokenType.RPAREN)
            )
        # module_code can be (None | CB1131)
        return module_code

    def module_description(self) -> Optional[Token]:
        # Parse module name until the numeric AU
        # e.g. Introduction to Computational Thinking
        module_description = []
        while not self.match_no_move(TokenType.NUMBER):
            token = self.current_token()
            self.move()
            module_description.append(token)
        module_description = flatten_tokens(TokenType.IDENTIFIER, module_description)
        return module_description

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

    def _mod_or(self) -> list[Token]:
        current_set = []
        current_set.append(self.module_code())
        while self.match(TokenType.AND):
            current_set.append(self.module_code())
        return current_set

    # This returns a Token.NUMBER of year of the pre-requisite
    def pre_requisite_year(self) -> Optional[Token]:
        initial_position = self.position
        if not self.match(TokenType.PREREQ):
            return None
        self.consume(TokenType.COLON, 'Expect colon after "Prerequisite"')

        # Within the year prerequisites, there are two formats
        # 1) Prerequisite: Year 3 standing
        # 2) Prerequisite: Study Year 3 standing
        # Note that I have not been able to find any nesting of years, i.e. Year 2 & Year 3 standing
        if self.match_identifier("Year") or self.match("Study"):
            # This moves past both Year and Study Year
            if self.previous_token().literal == "Study":
                self.move()
            year = self.consume(
                TokenType.NUMBER, "Expected a number after Year/Study Year"
            )
            self.consume(
                TokenType.STANDING, f"Expected a standing after Year/Study Year {year}"
            )
            return year

        self.set_position(initial_position)
        return None

    # This returns a list of the pre-requisite modules
    def pre_requisite_mods(self) -> Optional[list[Token]]:
        initial_position = self.position
        if not self.match(TokenType.PREREQ):
            return None
        self.consume(TokenType.COLON, 'Expect colon after "Prerequisite"')

        # This can either be a module prequisite or a year pre-requisite
        if self.match_no_move(TokenType.MODULE_CODE):
            prereq_mods = []
            # Append the first minimally required mods
            prereq_mods.append(self._mod_or())
            while self.match(TokenType.OR):
                prereq_mods.append(self._mod_or())
            return prereq_mods

        self.set_position(initial_position)
        return None

    def mutually_exclusive(self) -> Optional[list[Token]]:
        # If it does not start with "Mutually exclusive with"
        if not self.match_consecutive_identifiers(
            [TokenType.MUTUALLY, TokenType.EXCLUSIVE, TokenType.WITH]
        ):
            return None
        self.consume(TokenType.COLON, 'Expected colon after "Mutually Exclusive with"')

        exclusive_mods = []
        while self.match_no_move(TokenType.MODULE_CODE):
            module_code = self.module_code()
            exclusive_mods.append(module_code)
            self.match(TokenType.COMMA)

        print(exclusive_mods)
        return exclusive_mods

    def module(self) -> Optional[Module]:
        module_code = self.module_code()
        module_description = self.module_description()
        module_au = self.au()

        # Try to match for prerequisites, note that there are two choices here
        pre_requisites_year = self.pre_requisite_year()
        pre_requisites_mods = self.pre_requisite_mods()

        if pre_requisites_year is not None:
            print(pre_requisites_year)
        if pre_requisites_mods is not None:
            print(pre_requisites_mods)

        # Try to match for mutually exclusives
        mutually_exclusives = self.mutually_exclusive()

        # print(mutually_exclusives)

        module = tokens_to_module(
            module_code,
            module_description,
            module_au,
            mutually_exclusives,
            pre_requisites_year,
            pre_requisites_mods,
        )
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
