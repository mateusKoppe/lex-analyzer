import unittest

from finite_automaton.ndfa import NDFA


class TestNDFA(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.empty_ndfa = NDFA()

        self.grammar_if = {
            1: {"productions": {"i": {2}}, "is_final": False},
            2: {"productions": {"f": {3}}, "is_final": False},
            3: {"productions": {}, "is_final": True}
        }
        self.grammar_id = {
            1: {"productions": {
                "a": {2},
                "e": {2},
                "i": {2},
                "o": {2},
                "u": {2},
            }, "is_final": False},
            2: {"productions": {
                "a": {2},
                "e": {2},
                "i": {2},
                "o": {2},
                "u": {2}
            }, "is_final": True}
        }

    def test_from_token_else(self):
        ndfa = NDFA.from_token("else")

        self.assertFalse(ndfa.states["START"].is_final)
        self.assertFalse(ndfa.states["ELSE_1"].is_final)
        self.assertFalse(ndfa.states["ELSE_2"].is_final)
        self.assertFalse(ndfa.states["ELSE_3"].is_final)
        self.assertTrue(ndfa.states["ELSE"].is_final)

        self.assertIn("ELSE_1", ndfa.states["START"].transitions["e"])
        self.assertIn("ELSE_2", ndfa.states["ELSE_1"].transitions["l"])
        self.assertIn("ELSE_3", ndfa.states["ELSE_2"].transitions["s"])
        self.assertIn("ELSE", ndfa.states["ELSE_3"].transitions["e"])

        self.assertEqual(
            ndfa.initial_state,
            ndfa.states["START"]
        )

        self.assertEqual(ndfa.states["ELSE"].transitions, {})

    def test_from_grammar(self):
        ndfa = NDFA.from_grammar([
            "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
            "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε"
        ])
        self.assertEqual(
            ndfa.states,
            {
                1: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2},
                    },
                    "is_final": False
                },
                2: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2}
                    },
                    "is_final": True
                }
            }
        )

    def test_get_non_terminals(self):
        self.assertEqual(
            NDFA.get_non_terminals([
                "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
                "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε"
            ]),
            ["S", "A"]
        )

    def test_remove_useless_expression(self):
        self.assertEqual(
            NDFA.remove_useless_expressions({
                1: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2},
                    },
                    "is_final": False
                },
                2: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2}
                    },
                    "is_final": True
                },
                3: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {4},
                        "o": {4},
                        "u": {4}
                    },
                    "is_final": False
                },
                4: {
                    "productions": {
                        "a": {2},
                    },
                    "is_final": True
                }
            }),
            {
                1: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2},
                    },
                    "is_final": False
                },
                2: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2}
                    },
                    "is_final": True
                }
            }
        )

    def test_from_grammar(self):
        self.assertEqual(
            NDFA.from_grammar([
                "<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>",
                "<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε",
                "<B> ::= a<A> | e<A> | i<A> | o<A> | u<A>"
            ]).states,
            {
                1: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2},
                    },
                    "is_final": False
                },
                2: {
                    "productions": {
                        "a": {2},
                        "e": {2},
                        "i": {2},
                        "o": {2},
                        "u": {2},
                    },
                    "is_final": True
                }
            }
        )

    def test_get_alive_expressions(self):
        self.assertEqual(
            NDFA.get_alive_expressions({
                1: {'productions': {'a': {2}, 'e': {2}}, 'is_final': False},
                2: {'productions': {'a': {2}, 'e': {3}}, 'is_final': True},
                3: {'productions': {'a': {3}, 'e': {3}}, 'is_final': False}
            }),
            set([2, 1])
        )

        self.assertEqual(
            NDFA.get_alive_expressions({
                1: {'productions': {'a': {2}, 'e': {4}}, 'is_final': False},
                2: {'productions': {'a': {2}, 'e': {3}}, 'is_final': True},
                3: {'productions': {'a': {3}, 'e': {3}}, 'is_final': False},
                4: {'productions': {'a': {4}, 'e': {3}}, 'is_final': False},
                5: {'productions': {'a': {4}, 'e': {1}}, 'is_final': False}
            }),
            set([2, 1, 5])
        )

    def test_generate_grammar_remove_deads(self):
        self.assertEqual(
            NDFA.remove_dead_expressions({
                1: {'productions': {'a': {2}, 'e': {2}}, 'is_final': False},
                2: {'productions': {'a': {2}, 'e': {3}}, 'is_final': True},
                3: {'productions': {'a': {3}, 'e': {3}}, 'is_final': False}
            }),
            {
                1: {'productions': {'a': {2}, 'e': {2}}, 'is_final': False},
                2: {'productions': {'a': {2}}, 'is_final': True}
            }
        )


    def test_generate_expression(self):
        self.assertEqual(
            NDFA.generate_expression("<S> ::= a<A> | e<A> | i<B> | o<C> | ε"),
            {
                "productions": {
                    "a": {"A"},
                    "e": {"A"},
                    "i": {"B"},
                    "o": {"C"}
                },
                "is_final": True
            }
        )

        self.assertEqual(
            NDFA.generate_expression("<S> ::= a<A> | e<A> | i<B>"),
            {
                "productions": {
                    "a": {"A"},
                    "e": {"A"},
                    "i": {"B"},
                },
                "is_final": False
            }
        )

    def test_convert_non_terminals(self):
        self.assertEqual(
            NDFA.convert_non_terminals(
                {"a": {"A"}, "e": {"A"}, "i": {"B"}, "o": {"C"}},
                ["S", "A", "B", "C"]
            ),
            {"a": {2}, "e": {2}, "i": {3}, "o": {4}}
        )

    def test_is_expression(self):
        self.assertEqual(
            NDFA.is_expression("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            True
        )

        self.assertEqual(
            NDFA.is_expression('brown'),
            False
        )

    def test_is_sentence(self):
        self.assertEqual(
            NDFA.is_sentence('brown'),
            True
        )

        self.assertEqual(
            NDFA.is_sentence("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            False
        )


    def test_add_grammar_empty(self):
        ndfa = NDFA()

        ndfa.add_grammar({
            1: {"productions": {"i": {2}}, "is_final": False},
            2: {"productions": {"f": {3}}, "is_final": False},
            3: {"productions": {}, "is_final": True}
        })
        self.assertEqual(ndfa.states, {
            1: {"productions": {"i": {2}}, "is_final": False},
            2: {"productions": {"f": {3}}, "is_final": False},
            3: {"productions": {}, "is_final": True}
        })

    def test_add_grammar(self):
        self.empty_ndfa.add_grammar({
            1: {
                "productions": {
                    ".": {2}
                },
                "is_final": False
            },
            2: {
                "productions": {},
                "is_final": False
            }
        })
        self.empty_ndfa.add_grammar(self.grammar_if)

        self.assertEqual(
            self.empty_ndfa.states,
            {
                1: {
                    "productions": {
                        ".": {2},
                        "i": {3}
                    },
                    "is_final": False
                },
                2: {
                    "productions": {},
                    "is_final": False
                },
                3: {
                    "productions": {"f": {4}},
                    "is_final": False
                },
                4: {
                    "productions": {},
                    "is_final": True
                },
            }
        )

    def test_add_grammar_multiples(self):
        new_ndfa = NDFA()
        new_ndfa.add_grammar(self.grammar_if)
        new_ndfa.add_grammar(self.grammar_id)
        self.assertEqual(
            new_ndfa.states,
            {
                1: {
                    "productions": {
                        "i": {2, 4},
                        "a": {4},
                        "e": {4},
                        "o": {4},
                        "u": {4}
                    },
                    "is_final": False
                },
                2: {
                    "productions": {"f": {3}},
                    "is_final": False
                },
                3: {
                    "productions": {},
                    "is_final": True
                },
                4: {
                    "productions": {
                        "a": {4},
                        "e": {4},
                        "i": {4},
                        "o": {4},
                        "u": {4}
                    },
                    "is_final": True
                }
            }
        )
