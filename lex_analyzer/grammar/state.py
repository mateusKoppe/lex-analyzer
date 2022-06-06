from __future__ import annotations
from os import stat
from typing import Dict, Set
import re

class StateIndeterministicRuleError(Exception):
    pass

class State:

    def __init__(self, name: int = None, final_token: str = None) -> None:
        self.name = name
        self.final_token = final_token
        self.transitions: Dict[str, Set[int]] = {}

    def add_transition(self, terminal: str, state: State):
        try:
            self.transitions[terminal].add(state.name)
        except KeyError:
            self.transitions[terminal] = { state.name }

    def add_deterministic_transition(self, terminal: str, next_state: State):
        # TODO: check if this rule is right, maybe a terminal can exist without any key
        if terminal in self.transitions:
            raise StateIndeterministicRuleError(f"transition to {terminal} already determined")
            
        self.add_transition(terminal, next_state)

    def set_transition(self, terminal: str, next_state: set[str]):
        self.transitions[terminal] = next_state

    def get_transitions_by(self, terminal: str):
        try:
            return self.transitions[terminal]
        except KeyError:
            return set()

    def get_deterministic_transitions_by(self, terminal: str):
        transitions = self.get_transitions_by(terminal)
        if len(transitions) > 1:
            raise StateIndeterministicRuleError(f"State {self.name} has indeterminism for terminal {terminal}")
        elif len(transitions) == 0:
            return None
        return list(transitions)[0]

    def forget_state(self, state: State):
        for transition in self.transitions.values():
            transition.discard(state.name)

    def concat(self, state: State):
        if self.name != state.name:
            raise Exception(f"Cannot concat state {self.name} with {state.name}, states need to have the same name.")

        self.final_token = next((s for s in [self.final_token, state.final_token] if s), None)
        for terminal, transition in state.transitions.items():
            try:
                self.transitions[terminal].update(transition)
            except KeyError:
                self.transitions[terminal] = transition.copy()

    def copy(self) -> State:
        new_state = State(self.name, self.final_token)
        new_state.transitions = self.transitions.copy()
        for terminal, transition in new_state.transitions.items():
            new_state.transitions[terminal] = transition.copy()

        return new_state

    def rename_states(self, rename_map: Dict[int, int]):
        for terminal, transition in self.transitions.items():
            remaped = [rename_map.get(i, i) for i in list(transition)]
            self.transitions[terminal] = set(remaped)

    def pretty_output(self) -> str:
        if self.final_token:
            token_output = "*" if str(self.name) == self.final_token else f"({self.final_token})*"
            return f"{str(self.name)}{token_output}"
        return str(self.name)
