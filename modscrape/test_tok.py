#
# Modscrape
# Tests
# Token
#

from tok import Token, TokenType


def test_token_equal_value():
    # tests: tokens are equal by value
    token = Token(TokenType.IDENTIFIER, "test")
    assert token == Token(TokenType.IDENTIFIER, "test")
    assert Token(TokenType.AND, "test") != token
    assert Token(TokenType.IDENTIFIER, "nottest") != token
