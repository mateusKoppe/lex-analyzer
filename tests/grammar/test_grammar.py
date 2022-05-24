import unittest

from lex_analyzer.grammar.grammar import Grammar
from lex_analyzer.grammar.state import State


class TestGrammar(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.empty_gr = Grammar()

        self.if_gr = Grammar.from_regex_rule("IF -> if")

    def test_from_regex_rule(self):
        grammar = Grammar.from_regex_rule("IF -> if")

        self.assertIsNone(grammar.states[0].final_token)
        self.assertIsNone(grammar.states[1].final_token)
        self.assertEquals(grammar.states[2].final_token, "IF")

        self.assertEqual(grammar.states[0].transitions["i"], { 1 })
        self.assertEqual(grammar.states[1].transitions["f"], { 2 })
        self.assertEqual(grammar.states[2].transitions, {})

        self.assertEqual(
            grammar.initial_state,
            grammar.states[0]
        )

    def test_get_ended_expressions(self):
        dead_state = State()

        self.if_gr.add_state(dead_state)
        self.if_gr.add_transition(self.if_gr.states[2], dead_state, "f")

        self.assertEqual(
            self.if_gr.get_ended_expressions(),
            { 0, 1, 2 }
        )

    def test_remove_endless_expressions(self):
        dead_state = State()

        self.if_gr.add_state(dead_state)
        self.if_gr.add_transition(self.if_gr.states[2], dead_state, "f")

        self.if_gr.remove_endless_expressions()

        self.assertNotIn(dead_state, self.if_gr.states.values())
        self.assertNotIn(dead_state.name, self.if_gr.states[2].transitions["f"])

    def test_get_final_token(self):
        self.assertIsNone(self.if_gr.get_final_token(1))
        self.assertEquals(self.if_gr.get_final_token(2), "IF")
        # 
        self.assertIsNone(self.if_gr.get_final_token(100), "None for unexisting state")

    def test_forget_state(self):
        state = State()
        self.if_gr.add_state(state)

        self.if_gr.add_transition(self.if_gr.states[0], state, "o")
        self.if_gr.add_transition(self.if_gr.states[2], state, "o")
        self.if_gr.forget_state(state)

        self.assertNotIn(state.name, self.if_gr.states)
        self.assertNotIn(state.name, self.if_gr.states[0].transitions["o"])
        self.assertNotIn(state.name, self.if_gr.states[2].transitions["o"])

    def test_start_grammar(self):
        state = State()
        self.empty_gr.start_grammar(state)

        self.assertEqual(state.name, Grammar.INITIAL_STATE)
        self.assertEqual(self.empty_gr.states[Grammar.INITIAL_STATE], state)
        self.assertEqual(self.empty_gr.initial_state, state)

    def test_add_state(self):
        # TODO: test exception
        first_state = State()
        second_state = State()
        
        self.assertEquals(self.empty_gr.next_state_name, 1, "First common state should be 1")
        
        self.empty_gr.add_state(first_state)
        self.assertEquals(first_state.name, 1, "Should name state")
        self.assertEquals(self.empty_gr.next_state_name, 2, "Should increase next name")

        self.empty_gr.add_state(second_state)
        self.assertEquals(second_state.name, 2, "Should apply proper name")
        

    def test_add_state_named(self):
        state = State(42)
        self.empty_gr.add_state(state)
        
        self.assertEquals(state.name, 42, "Should not change name")
        self.assertEquals(state, self.empty_gr.states[state.name])

    def test_add_transition(self):
        state = State()
        initial_state = self.if_gr.initial_state
        self.if_gr.add_state(state)

        self.if_gr.add_transition(initial_state, state, "u")
        
        self.assertEquals(initial_state.transitions["u"], { state.name })

    def test_concat(self):
        fi_gr = Grammar.from_regex_rule("FI -> fi")
        self.if_gr.concat(fi_gr)

        self.assertEquals(self.if_gr.initial_state.get_transitions_by("i"), { 1 })
        self.assertEquals(self.if_gr.initial_state.get_transitions_by("f"), { 3 })

        self.assertEquals(self.if_gr.get_final_token(5), "FI")


