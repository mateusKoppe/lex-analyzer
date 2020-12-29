import unittest

from grammar import (
    generate_grammar_for_sentence,
    generate_grammar,
    get_non_terminals,
    generate_expression,
    convert_non_terminals
)


class TestGrammar(unittest.TestCase):
    def test_by_sentence(self):
        self.assertEqual(
            generate_grammar_for_sentence("se"),
            {
                1: [
                    ["s", 2],
                ],
                2: [
                    ["e", 3]
                ],
                3: [],
                "final": 3
            }
        )

        self.assertEqual(
            generate_grammar_for_sentence("se e"),
            {
                1: [
                    ["s", 2],
                ],
                2: [
                    ["e", 3]
                ],
                3: [
                    [" ", 4]
                ],
                4: [
                    ["e", 5]
                ],
                5: [],
                "final": 5
            }
        )

    def test_generate_grammar(self):
        self.assertEqual(
            generate_grammar([
                "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
                "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε"
            ]),
            {
                1: [
                    ["a", 2],
                    ["e", 2],
                    ["i", 2],
                    ["o", 2],
                    ["u", 2],
                ],
                2: [
                    ["a", 2],
                    ["e", 2],
                    ["i", 2],
                    ["o", 2],
                    ["u", 2]
                ],
                "final": 2
            }
        )

    def test_get_non_terminals(self):
        self.assertEqual(
            get_non_terminals([
                "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
                "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε"
            ]),
            ["S", "A"]
        )

    def test_generate_expression(self):
        self.assertEqual(
            generate_expression("<S> ::= a<A> | e<A> | i<B> | o<C> | ε"),
            {
                "productions": [["a", "A"], ["e", "A"], ["i", "B"], ["o", "C"]],
                "is_final": True
            }
        )

        self.assertEqual(
            generate_expression("<S> ::= a<A> | e<A> | i<B>"),
            {
                "productions": [["a", "A"], ["e", "A"], ["i", "B"]],
                "is_final": False
            }
        )
    
    def test_convert_non_terminals(self):
        self.assertEqual(
            convert_non_terminals(
                [["a", "A"], ["e", "A"], ["i", "B"], ["o", "C"]],
                ["S", "A", "B", "C"]
            ),
            [["a", 2], ["e", 2], ["i", 3], ["o", 4]]
        )
