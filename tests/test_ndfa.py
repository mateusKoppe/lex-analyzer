import unittest

from finite_automaton.ndfa import NDFA
from finite_automaton.state import State


class TestNDFA(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.empty_ndfa = NDFA()

        self.if_ndfa = NDFA.from_token("if")
        self.id_ndfa = NDFA.from_grammar([
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])

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
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])


        self.assertFalse(ndfa.states["START"].is_final)
        self.assertTrue(ndfa.states["ID"].is_final)

        self.assertIn("ID", ndfa.states["START"].transitions["a"])
        self.assertIn("ID", ndfa.states["START"].transitions["e"])
        self.assertIn("ID", ndfa.states["START"].transitions["u"])
        self.assertIn("ID", ndfa.states["ID"].transitions["a"])
        self.assertIn("ID", ndfa.states["ID"].transitions["e"])
        self.assertNotIn("u", ndfa.states["ID"].transitions)

        self.assertEqual(
            ndfa.initial_state,
            ndfa.states["START"]
        )

    def test_get_ended_expressions(self):
        dead_state = State("ENDLESS", False)

        self.if_ndfa.add_state(dead_state)
        self.if_ndfa.add_transition("IF", "ENDLESS", "f")

        self.assertEqual(
            self.if_ndfa.get_ended_expressions(),
            { "START", "IF_1", "IF" }
        )

    def test_remove_endless_expressions(self):
        dead_state = State("ENDLESS", False)

        self.if_ndfa.add_state(dead_state)
        self.if_ndfa.add_transition("IF", "ENDLESS", "f")

        self.if_ndfa.remove_endless_expressions()

        self.assertNotIn("ENDLESS", self.if_ndfa.states)
        self.assertNotIn("ENDLESS", self.if_ndfa.states["IF"].transitions["f"])

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
        ndfa.add_grammar(self.if_ndfa)

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
