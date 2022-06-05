from collections import deque
from typing import Dict

class RemapQueue:
    def __init__(self) -> None:
        self.discovered = set()
        self.to_discover = deque()
        self.state_to_create = 1
        self.remap_state: Dict[int, set[int]] = {}

    def push_to_discovery(self, state, merged_states = None):
        if not merged_states:
            merged_states = { state }

        if ((state, merged_states) not in self.to_discover) and state not in self.discovered:
            self.to_discover.append((state, merged_states))

    def create_state_to_discovery(self, states_to: set[int]) -> int:
        state_name = self.state_to_create
        self.state_to_create += 1
        self.push_to_discovery(state_name, states_to)

        return state_name
    
    def set_discovered(self, state):
        self.discovered.add(state)

    def set_remap(self, deterministic_state: int, merged_states: set[int]):
        self.remap_state[deterministic_state] = merged_states

    def pop_to_discover(self):
        try:
            return self.to_discover.popleft()
        except IndexError:
            return None

    def state_by_merged_states(self, states):
        try:
            return next(map_state for map_state, merged_states in self.remap_state.items() if merged_states==states)
        except StopIteration:
            deterministic_state = self.state_to_create
            self.set_remap(deterministic_state, states)
            self.state_to_create += 1
            return deterministic_state