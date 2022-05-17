
import unittest

from finite_automaton.dfa import DFA
from finite_automaton.ndfa import NDFA


class TestDFA(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.ndfa = NDFA()
        self.ndfa.add_grammar({
            1: {
                "productions": { "i": {2, 4}, "a": {4}, "e": {4} },
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
                "productions": { "a": {4}, "e": {4}, "i": {4}, "f": {2} },
                "is_final": True
            }
        })

    def test_index_to_production_name(self):
        self.assertEqual(DFA.index_to_production_name(1), "S")
        self.assertEqual(DFA.index_to_production_name(3), "B")
        self.assertEqual(DFA.index_to_production_name(26), "SS")
        self.assertEqual(DFA.index_to_production_name(55), "AD")

    def test_merge_productions(self):
        self.assertEqual(DFA.merge_productions(self.ndfa.states, {2, 4}), {
            "productions": {"f": {2, 3}, "a": {4}, "e": {4}, "i": {4}},
            "is_final": True,
            "from": {2, 4}
        })

    def test_search_production_rule(self):
        self.assertEqual(DFA.search_production_rule(
            {1: {}, 2: {"from": {2}}, 3: {"from": {1, 2}}},
            [2, 1]
         ), 3) 

        self.assertEqual(DFA.search_production_rule(
            {1: {}, 2: {"from": {2}}, 3: {"from": {1, 2}}},
            [3, 2, 1]
         ), None) 

    def test_eliminate_indeterminism(self):
        self.assertEqual(DFA.eliminate_indeterminism({
            1: { "productions": { "i": {2, 1}, "a": {2} },
                "is_final": False },
            2: { "productions": {"e": {2}},
                "is_final": True },
        }), {
            1: { "productions": { "i": {3}, "a": {2} },
                "is_final": False },
            2: { "productions": {"e": {2}},
                "is_final": True },
            3: { "productions": { "a": {2}, "e": {2}, "i": {3} },
                "is_final": True }
        })

        self.assertEqual(DFA.eliminate_indeterminism({
            1: { "productions": { "a": {1, 2}, "b": {1} },
                "is_final": False },
            2: { "productions": { "b": {3} },
                "is_final": False },
            3: { "productions": {},
                "is_final": True },
        }), {
            1: { "productions": { "a": {4}, "b": {1} },
                "is_final": False },
            4: { "productions": { "a": {4}, "b": {5} },
                "is_final": False },
            5: { "productions": { "a": {4}, "b": {1} },
                "is_final": True }
        })

    def test_generate_DFA(self):
        self.assertEqual(DFA.from_NDFA({
            1: { "productions": { "a": {1, 2}, "b": {1} },
                "is_final": False },
            2: { "productions": { "b": {3} },
                "is_final": False },
            3: { "productions": {},
                "is_final": True },
        }).states, {
            "S": { "productions": { "a": "C", "b": "S" },
                "is_final": False },
            "C": { "productions": { "a": "C", "b": "D" },
                "is_final": False },
            "D": { "productions": { "a": "C", "b": "S" },
                "is_final": True }
        })


