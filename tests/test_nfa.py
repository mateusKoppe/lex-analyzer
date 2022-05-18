import unittest

from finite_automaton.nfa import NFA
from finite_automaton.state import State


class TestNFA(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.empty_nfa = NFA()

        self.if_nfa = NFA.from_token("if")
        self.id_nfa = NFA.from_grammar([
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])

    def test_from_token_else(self):
        nfa = NFA.from_token("else")

        self.assertFalse(nfa.states["START"].is_final)
        self.assertFalse(nfa.states["ELSE_1"].is_final)
        self.assertFalse(nfa.states["ELSE_2"].is_final)
        self.assertFalse(nfa.states["ELSE_3"].is_final)
        self.assertTrue(nfa.states["ELSE"].is_final)

        self.assertIn("ELSE_1", nfa.states["START"].transitions["e"])
        self.assertIn("ELSE_2", nfa.states["ELSE_1"].transitions["l"])
        self.assertIn("ELSE_3", nfa.states["ELSE_2"].transitions["s"])
        self.assertIn("ELSE", nfa.states["ELSE_3"].transitions["e"])

        self.assertEqual(
            nfa.initial_state,
            nfa.states["START"]
        )

        self.assertEqual(nfa.states["ELSE"].transitions, {})

    def test_from_grammar(self):
        nfa = NFA.from_grammar([
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])


        self.assertFalse(nfa.states["START"].is_final)
        self.assertTrue(nfa.states["ID"].is_final)

        self.assertIn("ID", nfa.states["START"].transitions["a"])
        self.assertIn("ID", nfa.states["START"].transitions["e"])
        self.assertIn("ID", nfa.states["START"].transitions["u"])
        self.assertIn("ID", nfa.states["ID"].transitions["a"])
        self.assertIn("ID", nfa.states["ID"].transitions["e"])
        self.assertNotIn("u", nfa.states["ID"].transitions)

        self.assertEqual(
            nfa.initial_state,
            nfa.states["START"]
        )

    def test_get_ended_expressions(self):
        dead_state = State("ENDLESS", False)

        self.if_nfa.add_state(dead_state)
        self.if_nfa.add_transition("IF", "ENDLESS", "f")

        self.assertEqual(
            self.if_nfa.get_ended_expressions(),
            { "START", "IF_1", "IF" }
        )

    def test_remove_endless_expressions(self):
        dead_state = State("ENDLESS", False)

        self.if_nfa.add_state(dead_state)
        self.if_nfa.add_transition("IF", "ENDLESS", "f")

        self.if_nfa.remove_endless_expressions()

        self.assertNotIn("ENDLESS", self.if_nfa.states)
        self.assertNotIn("ENDLESS", self.if_nfa.states["IF"].transitions["f"])

    def test_is_expression(self):
        self.assertEqual(
            NFA.is_expression("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            True
        )

        self.assertEqual(
            NFA.is_expression('brown'),
            False
        )

    def test_is_sentence(self):
        self.assertEqual(
            NFA.is_sentence('brown'),
            True
        )

        self.assertEqual(
            NFA.is_sentence("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            False
        )


    def test_add_grammar_empty(self):
        nfa = NFA()
        nfa.add_grammar(self.if_nfa)

    def test_add_grammar(self):
        self.empty_nfa.add_grammar({
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
        self.empty_nfa.add_grammar(self.grammar_if)

        self.assertEqual(
            self.empty_nfa.states,
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
        new_nfa = NFA()
        new_nfa.add_grammar(self.grammar_if)
        new_nfa.add_grammar(self.grammar_id)
        self.assertEqual(
            new_nfa.states,
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
