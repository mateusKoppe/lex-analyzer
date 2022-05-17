from typing import Dict, Set


class State:
    def __init__(self, name: str, is_final: bool = True) -> None:
        self.name = name
        self.is_final = is_final
        self.transitions: Dict[str, Set[str]] = {}

    def add_transition(self, terminal: str, next_state: str):
        try:
            self.transitions[terminal].add(next_state)
        except KeyError:
            self.transitions[terminal] = { next_state }
