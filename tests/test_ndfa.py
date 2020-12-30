import unittest

from finite_automaton.grammar import generate_grammar_expression, generate_grammar_sentence
from finite_automaton.ndfa import add_grammar, generate_NDFA


class TestNDFA(unittest.TestCase):
    maxDiff = None

    def test_add_grammar(self):
        self.assertEqual(
            add_grammar({
                1: {
                    "productions": {
                        ".": [2]
                    },
                    "is_final": False
                },
                2: {
                    "productions": {},
                    "is_final": False
                }
            }, generate_grammar_sentence("if")),
            {
                1: {
                    "productions": {
                        ".": [2],
                        "i": [3]
                    },
                    "is_final": False
                },
                2: {
                    "productions": {},
                    "is_final": False
                },
                3: {
                    "productions": {"f": [4]},
                    "is_final": False
                },
                4: {
                    "productions": {},
                    "is_final": True
                },
            }
        )

    def test_add_grammar_empry(self):
        self.assertEqual(
            add_grammar({}, generate_grammar_sentence("if")),
            {
                1: {
                    "productions": {
                        "i": [2]
                    },
                    "is_final": False
                },
                2: {
                    "productions": {"f": [3]},
                    "is_final": False
                },
                3: {
                    "productions": {},
                    "is_final": True
                },
            }
        )

    def test_generate_NDFA_simple(self):
        self.assertEqual(
            generate_NDFA([generate_grammar_sentence("if")]),
            {
                1: {
                    "productions": {
                        "i": [2]
                    },
                    "is_final": False
                },
                2: {
                    "productions": {
                        "f": [3]
                    },
                    "is_final": False
                },
                3: {"productions": {}, "is_final": True}
            }
        )

    def test_generate_NDFA(self):
        self.assertEqual(
            generate_NDFA([
                generate_grammar_sentence("if"),
                generate_grammar_expression([
                    "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
                    "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε"
                ]),
                generate_grammar_sentence("end")
            ]),
            {
                1: {
                    "productions": {
                        "i": [2, 4],
                        "a": [4],
                        "e": [4, 5],
                        "o": [4],
                        "u": [4]
                    },
                    "is_final": False
                },
                2: {
                    "productions": {"f": [3]},
                    "is_final": False
                },
                3: {
                    "productions": {},
                    "is_final": True
                },
                4: {
                    "productions": {
                        "a": [4],
                        "e": [4],
                        "i": [4],
                        "o": [4],
                        "u": [4]
                    },
                    "is_final": True
                },
                5: {
                    "productions": {"n": [6]},
                    "is_final": False
                },
                6: {
                    "productions": {"d": [7]},
                    "is_final": False
                },
                7: {
                    "productions": {},
                    "is_final": True
                },
            }
        )
