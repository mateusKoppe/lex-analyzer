import unittest

from finite_automaton.grammar.grammar import Grammar
from finite_automaton.grammar.state import State


class TestGrammar(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.empty_nfa = Grammar()

        self.if_nfa = Grammar.from_token("if")
        self.id_nfa = Grammar.from_raw_grammar([
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])

    def test_from_token_else(self):
        nfa = Grammar.from_token("else")

        self.assertIsNone(nfa.states["START"].final_token)
        self.assertIsNone(nfa.states["ELSE_1"].final_token)
        self.assertIsNone(nfa.states["ELSE_2"].final_token)
        self.assertIsNone(nfa.states["ELSE_3"].final_token)
        self.assertEquals(nfa.states["ELSE"].final_token, "ELSE")

        self.assertIn("ELSE_1", nfa.states["START"].transitions["e"])
        self.assertIn("ELSE_2", nfa.states["ELSE_1"].transitions["l"])
        self.assertIn("ELSE_3", nfa.states["ELSE_2"].transitions["s"])
        self.assertIn("ELSE", nfa.states["ELSE_3"].transitions["e"])

        self.assertEqual(
            nfa.initial_state,
            nfa.states["START"]
        )

        self.assertEqual(nfa.states["ELSE"].transitions, {})

    def test_from_raw_grammar(self):
        nfa = Grammar.from_raw_grammar([
            "<START> ::= a<ID> | e<ID> | u<ID>",
            "<ID> ::= a<ID> | e<ID> | ε"
        ])


        self.assertIsNone(nfa.states["START"].final_token)
        self.assertEqual(nfa.states["ID"].final_token, "ID")

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
            Grammar.is_expression("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            True
        )

        self.assertEqual(
            Grammar.is_expression('brown'),
            False
        )

    def test_is_sentence(self):
        self.assertEqual(
            Grammar.is_sentence('brown'),
            True
        )

        self.assertEqual(
            Grammar.is_sentence("<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>"),
            False
        )