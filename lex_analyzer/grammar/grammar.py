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
    REGEX_RULE = r"(\w+)\s*->\s*(.+)\n?"

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
    def NFA_to_DFA(cls, nfa: Grammar) -> Grammar:
        dfa = cls()
        dfa.next_state_name = 0
        
        remap_table: Dict[int, set[int]] = {}

        dfa.initial_state = dfa.create_state()
        dfa.initial_state.final_token = nfa.initial_state.final_token

        remap_table[dfa.initial_state.name] = { nfa.initial_state.name }
        to_discovery: list[State] = [ dfa.initial_state ]

        while True:
            try:
                discovering_state = to_discovery.pop(0)
            except IndexError:
                break

            discovering_states = remap_table[discovering_state.name]
            discovering_state.final_token = next((nfa.get_final_token(s) for s in list(discovering_states) if nfa.get_final_token(s)), None)

            for discovering in discovering_states:
                for terminal, transition_to in nfa.states[discovering].transitions.items():
                    try:
                        remaped_name = next(s for s, c in remap_table.items() if c == transition_to)
                        remaped_state = dfa.states[remaped_name]
                    except StopIteration:
                        remaped_state = dfa.create_state()
                        remap_table[remaped_state.name] = transition_to
                        to_discovery.append(remaped_state)

                    try:
                        discovering_state.add_deterministic_transition(terminal, remaped_state)
                    except StateIndeterministicRuleError:
                        # TODO: This generate unacessible states
                        remaped_transitions_states = discovering_state.get_transitions_by(terminal)
                        remaped_transitions_states = remaped_transitions_states.union({ remaped_state.name })
                        transition_states = set()
                        for remaped_state in remaped_transitions_states:
                            transition_states = remap_table[remaped_state].union(transition_states)

                        try:
                            remaped_state = next((s for s, c in remap_table.items() if c == transition_states))
                        except StopIteration:
                            remaped_state = dfa.create_state()
                            remap_table[remaped_state.name] = transition_states
                            to_discovery.append(remaped_state)

                        discovering_state.set_transition(terminal, { remaped_state.name })
                        
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

    def forget_state(self, dead_state: int):
        del self.states[dead_state]
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

    def create_state(self):
        state = State(self.next_state_name)
        self.next_state_name += 1
        self.add_state(state)
        return state

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

    def set_follow(self, follow_grammar: Grammar) -> None:
        remap_states: Dict[int, State] = {}
        initial_follow = follow_grammar.initial_state

        final_states = [state for state in self.states.values() if state.final_token]

        # Add states
        for state in follow_grammar.states.values():
            if state == initial_follow:
                continue

            new_state = self.create_state()
            new_state.final_token = state.final_token
            remap_states[state.name] = new_state

        # Remap transitions
        for state in follow_grammar.states.values():
            if state == initial_follow:
                continue

            for terminal, transitions in state.transitions.items():
                for transition in list(transitions):
                    remaped = remap_states[state.name]
                    remaped.add_transition(terminal, remap_states[transition])

        # final state to the new follow state
        for final_state in final_states:
            final_state.final_token = None
            for terminal, transitions in initial_follow.transitions.items():
                for transition in list(transitions):
                    final_state.add_transition(terminal, remap_states[transition])
