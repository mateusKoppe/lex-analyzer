from __future__ import annotations
import re
from collections import deque
from typing import Dict, List
from terminaltables import AsciiTable
from enum import Enum

from finite_automaton.grammar.state import State
from finite_automaton.grammar.remap_queue import RemapQueue

class GrammarType(Enum):
    NFA = 1
    DFA = 2

class Grammar:
    INITIAL_STATE = "START"

    @classmethod
    def from_token(cls, word: str):
        nfa = cls(GrammarType.DFA)
        
        state_final = State(word.upper(), word.upper())
        last_created_state = state_final
        created = 1
        for letter in reversed(word):
            nfa.add_state(last_created_state)
            name = f"{word.upper()}_{len(word) - created}"
            state = State(name)
            state.add_transition(letter, last_created_state.name)
            last_created_state = state
            
            created += 1

        nfa.start_grammar(last_created_state)

        return nfa

    @classmethod
    def from_raw_grammar(cls, lines: List[str]):
        nfa = cls()
        
        lines_deque = deque(lines)

        initial_state = State.from_raw(lines_deque.popleft())
        nfa.start_grammar(initial_state)

        for line in lines_deque:
            state = State.from_raw(line)
            nfa.add_state(state)

        nfa.remove_endless_expressions()

        return nfa

    @classmethod
    # TODO: Handle epsilon moves
    def NFA_to_DFA(cls, nfa: Grammar) -> Grammar:
        dfa = cls()

        remap_queue = RemapQueue()
        remap_queue.push_to_discovery(nfa.initial_state.name)
        state_tuple = remap_queue.pop_to_discover()
        while state_tuple:
            state_name, states_to = state_tuple
            final_token = next((nfa.states[s].final_token for s in list(states_to)), None)
            new_state = State(state_name, final_token)
            dfa.add_state(new_state)
            remap_queue.set_discovered(state_name)

            for state_to in list(states_to):
                state = nfa.states[state_to]

                for terminal, states in state.transitions.items():
                    is_deterministic = len(states) == 1
                    if is_deterministic:
                        transition_state = list(states)[0]
                        # TODO: This can still cause indeterminism 
                        new_state.add_transition(terminal, transition_state)
                        remap_queue.push_to_discovery(transition_state)
                    else:
                        maped_state = remap_queue.state_by_merged_states(states)
                        new_state.add_transition(terminal, maped_state)

            state_tuple = remap_queue.pop_to_discover()

        dfa.initial_state = dfa.states[nfa.initial_state.name]
        return dfa

    @staticmethod
    def is_expression(raw):
        return bool(re.match(State.GRAMMAR_REGEX, raw))      


    @staticmethod
    def is_sentence(raw):
        return not Grammar.is_expression(raw)

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

    def __init__(self, type: GrammarType = None):
        self.initial_state = None
        self.states: Dict[str, State] = {} 
        self.type = GrammarType.NFA
        if type:
            self.type = type

    def remove_endless_expressions(self):
        states = set(self.states.keys())
        dead_states = states - self.get_ended_expressions()
        
        for dead_state in dead_states:
            self.forget_state(dead_state)

    def forget_state(self, dead_state: str):
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

        self.states[state.name] = state

    def add_transition(self, from_state: str, to_state: str, terminal: str):
        self.states[from_state].add_transition(terminal, to_state)

    def concat(self, nfa: Grammar):
        for state in nfa.states.values():
            if state.name == Grammar.INITIAL_STATE:
                continue

            self.add_state(state.copy())
        self.initial_state.concat(nfa.initial_state)

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
                    row.append(
                        state.name + (
                            f"({state.final_token})*" if state.final_token else ""
                        )
                    )
                    continue

                try:
                    row.append(", ".join(state.transitions[column]))
                except KeyError:
                    row.append('-')
            rows.append(row)

        return AsciiTable(rows).table