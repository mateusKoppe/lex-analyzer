import unittest

from finite_automaton.ndfa import add_grammar, generate_NDFA


class TestNDFA(unittest.TestCase):
    def setUp(self):
        self.grammar_if = {
            1: {"productions": {"i": {2}}, "is_final": False},
            2: {"productions": {"f": {3}}, "is_final": False},
            3: {"productions": {}, "is_final": True}
        }
        self.grammar_expression = {
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

    def test_add_grammar(self):
        self.assertEqual(
            add_grammar({
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
            }, self.grammar_if),
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

    def test_add_grammar_empry(self):
        self.assertEqual(
            add_grammar({}, self.grammar_if),
            {
                1: {
                    "productions": {
                        "i": {2}
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
            }
        )

    def test_generate_NDFA_simple(self):
        self.assertEqual(
            self.grammar_if,
            {
                1: {"productions": {"i": {2}}, "is_final": False},
                2: {"productions": {"f": {3}}, "is_final": False},
                3: {"productions": {}, "is_final": True}
            }
        )

    def test_generate_NDFA(self):
        self.assertEqual(
            generate_NDFA([
                self.grammar_if,
                self.grammar_expression
            ]),
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
