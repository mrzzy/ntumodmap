#
# Parser
# Parses a list[list[Token]] into list[Module]
# The information the modules have in them should be
# further analyzed and turned into a graph
# This will just produce a flat structure of [Modude]
#

from typing import Callable, Optional, TypeVar, cast

from module import Course, Module, ModuleCode
from tok import Token, TokenType, flatten_tokens
from pprint import pprint

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
            return None
        return res

    return contextual_wrapper(parser)


def tokens_to_module(
    module_code: ModuleCode,
    module_title: Token,
    module_au: Token,
    module_pass_fail: bool,
    module_pre_requisite_year: Optional[Token],
    module_pre_requisite_mods: list[list[ModuleCode]],
    module_mutually_exclusives: list[ModuleCode],
    module_reject_courses: list[Course],
) -> Module:
    title = module_title.literal
    au = float(module_au.literal)

    # TODO: To be filled in
    rejects_modules: list[ModuleCode] = []
    rejects_courses: list[Course] = module_reject_courses
    allowed_courses: list[Course] = []
    is_bde = False

    assert isinstance(title, str) and isinstance(au, float)

    return Module(
        module_code,
        title,
        au,
        module_mutually_exclusives,
        # parse needs_year as int if set
        (
            int(module_pre_requisite_year.literal)
            if module_pre_requisite_year is not None
            else None
        ),
        module_pre_requisite_mods,
        rejects_modules,
        rejects_courses,
        allowed_courses,
        is_bde,
        module_pass_fail,
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

    def current_token(self, peek=0) -> Token:
        return self.tokens[self.paragraph][self.position + peek]

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
        if current_token.token_type == token_type:
            return True
        # All other cases are false
        return False

    # Takes in a TokenType, if the current token is of the same TokenType
    # it will move the position up
    def match(self, token_type: TokenType) -> bool:
        current_token = self.current_token()
        if current_token.token_type == token_type:
            self.move()
            return True
        # All other cases are false
        return False

    # Takes in a list of [TokenType], if the current token is of the same TokenType
    # it will move the position up
    def match_multi(self, token_types: list[TokenType]) -> bool:
        current_token = self.current_token()
        for token_type in token_types:
            if cast(Token, current_token).token_type != token_type:
                return False
            self.move()
            current_token = self.current_token()
        return True

    def match_identifier(self, identifier_literal: str) -> bool:
        current_token = self.current_token()
        if current_token.token_type != TokenType.IDENTIFIER:
            return False
        if current_token.literal == identifier_literal:
            self.move()
            return True
        return False

    def match_consecutive(self, token_types: list[TokenType]) -> bool:
        for token_type in token_types:
            if not self.match(token_type):
                return False
        return True

    def match_consecutive_literals(
        self, token_types: list[TokenType], token_literals: list[str]
    ) -> bool:
        assert len(token_types) == len(token_literals)
        for token_type, token_literal in zip(token_types, token_literals):
            token = self.current_token()
            if not self.match(token_type):
                return False
            if cast(Token, token).literal != token_literal:
                return False
        return True

    def match_consecutive_identifiers(self, token_literals: list[str]) -> bool:
        initial_position = self.position
        for token_literal in token_literals:
            if not self.match_identifier(token_literal):
                self.set_position(initial_position)
                return False
        return True

    def raise_error(self, expected_token_type: TokenType) -> Exception:
        current_token = self.current_token()
        raise Exception(
            f"Error: expected {expected_token_type} but received {current_token.token_type}",
        )

    def consume(self, token_type: TokenType, error: str) -> Token:
        try_match = self.match(token_type)
        # If it failed to match: return an error
        if not try_match:
            self.raise_error(token_type)
        # desired tokens was just matched, so retrieving previous should not return None
        return cast(Token, self.previous_token())

    def consume_multi(self, token_types: list[TokenType], error: str) -> Token:
        try_match = self.match_multi(token_types)
        if not try_match:
            current_token = self.current_token()
            raise Exception(
                f"Error: expected {token_types} but received {current_token.token_type}",
            )
        # desired tokens was just matched, so retrieving previous should not return None
        return cast(Token, self.previous_token())

    def module_code(self) -> ModuleCode:
        # e.g. CB1131, SC1005, SC1007
        module_code_token = self.consume(
            TokenType.MODULE_CODE, "Expected an module code to start off a module"
        )
        module_code = ModuleCode(module_code_token.literal)

        # If the module code is e.g. 'MH1812(Corequisite)', this will catch that and parse it in
        if self.match(TokenType.LPAREN):
            if self.match_consecutive([TokenType.COREQ, TokenType.RPAREN]):
                module_code.is_corequisite = True
            else:
                self.move()
                misc = []
                while not self.match(TokenType.RPAREN):
                    # since we are moving forwards, previous token can never be None
                    previous_token = cast(Token, self.previous_token())
                    if previous_token.token_type != TokenType.LPAREN:
                        misc.append(previous_token.literal)
                    self.move()
                module_code.misc = " ".join(misc)

        # module_code can be (None | ModuleCode(CB1131))
        return module_code

    def course(self) -> Course:
        # TODO: Concatenate the course code into one,
        # can possible be MS-2ndMaj/Spec, which is multiple identifier tokens
        course_code = self.consume(
            TokenType.IDENTIFIER, "Expected an identifier for a course"
        )

        alt_course_code = None
        from_year = None
        to_year = None
        is_direct_entry = None

        # Possible cases: ENG(ENE)(2018-onwards)
        # There are up to 3 possible parenthesis here - just match them all
        for _ in range(3):
            if self.match(TokenType.LPAREN):
                # Check for alternate representations
                if self.match_consecutive_identifiers(["Direct", "Entry"]):
                    is_direct_entry = True
                elif self.match_consecutive_identifiers(["Non", "Direct", "Entry"]):
                    is_direct_entry = False
                elif self.match(TokenType.IDENTIFIER):
                    previous_token = cast(Token, self.previous_token())
                    alt_course_code = previous_token.literal
                    # Close off the parenthesis
                elif self.match(TokenType.NUMBER):
                    previous_token = cast(Token, self.previous_token())
                    from_year = int(previous_token.literal)
                    # Optional dash
                    if self.match(TokenType.DASH):
                        # Expect either a number or a "onwards"
                        if self.match_identifier("onwards"):
                            to_year = 9999
                        elif self.match(TokenType.NUMBER):
                            to_year = int(self.current_token().literal)
                self.consume(TokenType.RPAREN, "Expected a ')' to close off '('")

        return Course(
            course=course_code.literal,
            is_direct_entry=None,
            from_year=from_year,
            to_year=to_year,
            alt_course=alt_course_code,
        )

    def pass_fail(self) -> bool:
        initial_position = self.position
        found = self.match_multi([TokenType.GRADE, TokenType.TYPE])
        if found:
            self.consume(TokenType.COLON, "Expected ':' after 'Grade Type'")
            self.consume(TokenType.PASS, "Expected 'Pass' after 'Grade Type:'")
            self.consume(TokenType.SLASH, "Expected '/' after 'Grade Type: Pass'")
            self.consume(
                TokenType.FAIL, "Expected 'Fail' after 'Grade Type: Pass/Fail'"
            )
            return True
        self.set_position(initial_position)
        return False

    def module_description(self) -> Token:
        # Parse module name until the numeric AU
        # e.g. Introduction to Computational Thinking
        module_description = []
        while not self.match_no_move(TokenType.NUMBER):
            token = self.current_token()
            self.move()
            module_description.append(token)
        return flatten_tokens(TokenType.IDENTIFIER, module_description)

    def au(self) -> Token:
        number = self.consume(TokenType.NUMBER, "Expected a number to indicate AUs")

        aus = [number]
        while not self.match(TokenType.AU):
            token = self.current_token()
            self.move()
            aus.append(token)

        return flatten_tokens(TokenType.AU, aus, interval="")

    def _mod_and(self) -> list[ModuleCode]:
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
        if self.match_identifier("Year") or self.match_identifier("Study"):
            # This moves past both Year and Study Year
            previous_token = self.previous_token()
            if previous_token is not None and previous_token.literal == "Study":
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

    # This returns a list of list of the pre-requisite modules
    # Each nested list represents set of module(s) that can be taken to satisfy prerequisites
    def pre_requisite_mods(self) -> list[list[ModuleCode]]:
        initial_position = self.position
        if not self.match(TokenType.PREREQ):
            return []
        self.consume(TokenType.COLON, 'Expect colon after "Prerequisite"')

        # This can either be a module prerequisite or a year pre-requisite
        if self.match_no_move(TokenType.MODULE_CODE):
            prereq_mods = []
            # Append the first minimally required mods
            prereq_mods.append(self._mod_and())
            while self.match(TokenType.OR):
                prereq_mods.append(self._mod_and())
            return prereq_mods

        self.set_position(initial_position)
        return []

    def mutually_exclusive(self) -> list[ModuleCode]:
        # If it does not start with "Mutually exclusive with"
        if not self.match_consecutive_identifiers(
            [TokenType.MUTUALLY.value, TokenType.EXCLUSIVE.value, TokenType.WITH.value]
        ):
            return []
        self.consume(TokenType.COLON, 'Expected colon after "Mutually Exclusive with"')

        exclusive_mods = []
        while self.match_no_move(TokenType.MODULE_CODE):
            module_code = self.module_code()
            exclusive_mods.append(module_code)
            self.match(TokenType.COMMA)

        return exclusive_mods

    def not_available_to_programme(self) -> list[Course]:
        if not self.match_consecutive_identifiers(
            [
                TokenType.NOT.value,
                TokenType.AVAIL.value,
                TokenType.TO.value,
                TokenType.PROGRAMME.value,
            ]
        ):
            return []
        # There's always a ':' after 'Not available to Programme'
        self.consume(TokenType.COLON, "Expected ':' after 'Not available to Programme'")

        courses: list[Course] = []
        while course := self.course():
            courses.append(course)
            if self.current_token().token_type == TokenType.COMMA:
                self.move()
            else:
                break
        return courses

    def not_available_to_programme_with(self) -> list[Course]:
        return []

    def not_offered_as_bde_or_ue(self) -> Optional[Token]:
        if self.match_consecutive(
            [
                TokenType.NOT,
                TokenType.OFFERED,
                TokenType.AS,
                TokenType.BROADENING,
                TokenType.IDENTIFIER,
                TokenType.DEEPENING,
                TokenType.ELECTIVE,
            ]
        ):
            return Token(
                TokenType.NOT_OFFERED_AS_BDE, TokenType.NOT_OFFERED_AS_BDE.value
            )
        if self.match_consecutive_literals(
            [
                TokenType.NOT,
                TokenType.OFFERED,
                TokenType.AS,
                TokenType.UNRESTRICTED,
                TokenType.ELECTIVE,
            ],
            [
                TokenType.NOT.value,
                TokenType.OFFERED.value,
                TokenType.AS.value,
                TokenType.UNRESTRICTED.value,
                TokenType.ELECTIVE.value,
            ],
        ):
            return Token(TokenType.NOT_OFFERED_AS_UE, TokenType.NOT_OFFERED_AS_UE.value)
        return None

    def module(self) -> Optional[Module]:
        module_code = self.module_code()
        module_description = self.module_description()
        module_au = self.au()
        pass_fail = self.pass_fail()

        # Try to match for prerequisites, note that there are two choices here
        pre_requisites_year = self.pre_requisite_year()
        pre_requisites_mods = self.pre_requisite_mods()

        # Try to match for mutually exclusives
        mutually_exclusives = self.mutually_exclusive()

        # Try to match Not available to Programme:
        not_available_to_programme = self.not_available_to_programme()

        # Try to match Not available to Programme with:
        not_available_to_programme_with = self.not_available_to_programme_with()

        # Try to match Not available as PE to Programme with:
        # Note that PE stands for Prescribed Elective

        # Not offered as BDE or UE
        # not_offered_as_bde_or_ue = self.not_offered_as_bde_or_ue()

        module = tokens_to_module(
            module_code,
            module_description,
            module_au,
            pass_fail,  # module pass fail
            pre_requisites_year,
            pre_requisites_mods,
            mutually_exclusives,
            not_available_to_programme,
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
