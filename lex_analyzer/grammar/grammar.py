from __future__ import annotations
import re
from collections import deque
from typing import Dict, List
from terminaltables import AsciiTable
from enum import Enum

from lex_analyzer.grammar.state import State, StateIndeterministicRuleError
from lex_analyzer.grammar.remap_queue import RemapQueue

class GrammarInvalidRule(Exception):
    pass

class GrammarType(Enum):
    NFA = 1
    DFA = 2

class Grammar:
    INITIAL_STATE = 0
    REGEX_RULE = r"(\w+)\s*->\s*(.+)"

    @classmethod
    def from_regex_rule(cls, rule: str) -> Grammar:
        match = re.search(cls.REGEX_RULE, rule)
        if not match:
            raise GrammarInvalidRule(f"rule {rule} is invalid.")
        token, regex = match.groups()
        grammar = cls()

        prev = State()
        grammar.start_grammar(prev)
        for terminal in regex:
            state = State()
            grammar.add_state(state)
            prev.add_transition(terminal, state)
            
            prev = state

        prev.final_token = token
        return grammar

    @classmethod
    # TODO: Refactor NFA
    def NFA_to_DFA(cls, nfa: Grammar) -> Grammar:
        dfa = cls()

        remap_queue = RemapQueue()
        remap_queue.push_to_discovery(nfa.initial_state.name)
        state_tuple = remap_queue.pop_to_discover()
        while state_tuple:
            state_name, states_to = state_tuple
            final_token = next((nfa.get_final_token(s) for s in list(states_to) if nfa.get_final_token(s)), None)
            new_state = State(state_name, final_token)
            dfa.add_state(new_state)
            remap_queue.set_discovered(state_name)

            for state_to in list(states_to):
                state = nfa.states[state_to]

                for terminal, states in state.transitions.items():
                    is_deterministic = len(states) == 1
                    state_to_map = list(states)[0]
                    try:
                        if not is_deterministic:
                            state_to_map = remap_queue.state_by_merged_states(states)
                                                        
                        new_state.add_deterministic_transition(terminal, state_to_map)
                        remap_queue.push_to_discovery(state_to_map, states)
                    except StateIndeterministicRuleError:
                        transition_states = new_state.get_transitions_by(terminal)
                        next_states = transition_states.union({ state_to_map })
                        state_to_map = remap_queue.state_by_merged_states(next_states)
                        new_state.set_transition(terminal, state_to_map)
                        remap_queue.push_to_discovery(state_to_map, next_states)

            state_tuple = remap_queue.pop_to_discover()

        dfa.initial_state = dfa.states[nfa.initial_state.name]
        return dfa

    def __init__(self, type: GrammarType = GrammarType.NFA):
        # TODO: Convert initial_state to str
        self.initial_state = None
        self.states: Dict[int, State] = {} 
        self.type = type
        self.next_state_name = 1

    def get_final_token(self, state_name: int) -> str | None:
        try:
            return self.states[state_name].final_token
        except KeyError:
            return None

    def get_ended_expressions(self):
        ending_expressions = set([state.name for state in self.states.values() if state.final_token])

        new_ending_found = True
        while (new_ending_found):
            new_ending_found = False
            for index, state in self.states.items():
                if (index in ending_expressions):
                    continue

                for non_terminals in state.transitions.values():
                    intersection = set(ending_expressions) & set(non_terminals)
                    if len(intersection):
                        ending_expressions.add(index)
                        new_ending_found = True

        return ending_expressions

    def remove_endless_expressions(self):
        states = set(self.states.keys())
        dead_states = states - self.get_ended_expressions()
        
        for dead_state in dead_states:
            self.forget_state(dead_state)

    def forget_state(self, dead_state: State):
        del self.states[dead_state.name]
        for state in self.states.values():
            state.forget_state(dead_state)

    def start_grammar(self, state: State):
        state.name = Grammar.INITIAL_STATE
        self.add_state(state)
        self.initial_state = state

    def add_state(self, state: State):
        if state.name in self.states:
            raise Exception(f"State {state.name} already exist")

        if state.name is None:
            state.name = self.next_state_name
            self.next_state_name += 1

        self.states[state.name] = state

    def add_transition(self, from_state: State, to_state: State, terminal: str):
        from_state.add_transition(terminal, to_state)

    def concat(self, nfa: Grammar):
        copied_initial_state = nfa.initial_state.copy()

        if not self.initial_state:
            self.start_grammar(copied_initial_state)

        added_states = [copied_initial_state]
        rename_rules = {}

        for state in nfa.states.values():
            if state.name == Grammar.INITIAL_STATE:
                continue

            copied_state = state.copy()
            copied_state.name = None
            added_states.append(copied_state)
            self.add_state(copied_state)
            rename_rules[state.name] = copied_state.name

        for state in added_states:
            state.rename_states(rename_rules)

        self.initial_state.concat(copied_initial_state)

    def get_transition_state(self, state_origin: State, terminal: str) -> State | None:
        state = state_origin.get_deterministic_transitions_by(terminal)
        try:
            return self.states[state]
        except IndexError:
            return None
        except KeyError:
            return None

    def asci_table(self):
        header = ['/']
        for state in self.states.values():
            for letter in state.transitions.keys():
                try:
                    header.index(letter)
                except ValueError:
                    header.append(letter)
        rows = [header]

        for state in self.states.values():
            row = []
            for column in header:
                if column == '/':
                    row.append(state.pretty_output())
                    continue

                try:
                    row.append(", ".join(map(str, state.transitions[column])))
                except KeyError:
                    row.append('-')
            rows.append(row)

        return AsciiTable(rows).table