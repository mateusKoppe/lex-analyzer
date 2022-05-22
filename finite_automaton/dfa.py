from __future__ import annotations
from collections import deque
from typing import Dict
from terminaltables import AsciiTable

from finite_automaton.nfa import NFA
from finite_automaton.state import State

class RemapQueue:
    def __init__(self) -> None:
        self.discovered = set()
        self.to_discover = deque()
        self.state_to_create = 1
        self.remap_state: Dict[str, set[str]] = {}

    def push_to_discovery(self, state, merged_states = None):
        if not merged_states:
            merged_states = { state }

        if ((state, merged_states) not in self.to_discover) and state not in self.discovered:
            self.to_discover.append((state, merged_states))
    
    def set_discovered(self, state):
        self.discovered.add(state)

    def set_remap(self, deterministic_state, merged_states):
        self.remap_state[deterministic_state] = merged_states

    def pop_to_discover(self):
        try:
            next_tuple = self.to_discover.popleft()
            return next_tuple
        except IndexError:
            return None

    def state_by_merged_states(self, states):
        try:
            map_state = [map_state for map_state, merged_states in self.remap_state.items() if merged_states==states]
            return map_state[0]
        except IndexError:
            deterministic_state = str(self.state_to_create)
            
            self.push_to_discovery(deterministic_state, states)
            self.set_remap(deterministic_state, states)
            self.state_to_create += 1
            return deterministic_state


class DFA:
    @classmethod
    def from_NFA(cls, nfa: NFA) -> DFA:
        dfa = cls()

        remap_queue = RemapQueue()
        remap_queue.push_to_discovery(nfa.initial_state.name)
        state_tuple = remap_queue.pop_to_discover()
        while state_tuple:
            state_name, states_to = state_tuple
            new_state = State(state_name)
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

    def __init__(self):
        self.states: Dict[str, State] = {}
        self.initial_state: State = None

    def add_state(self, state: State):
        if state.name in self.states:
            raise Exception(f"State {state.name} already exist")

        self.states[state.name] = state

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
                        "*" if state.is_final else ""
                    ))
                    continue

                try:
                    row.append(", ".join(state.transitions[column]))
                except KeyError:
                    row.append('-')
            rows.append(row)

        return AsciiTable(rows).table
