from finite_automaton.ndfa import NDFA
from finite_automaton.dfa import DFA


def get_inputs():
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return lines


def generate_ndfa(lines):
    ndfa = NDFA()
    acc_lines = []
    for line in lines:
        if NDFA.is_expression(line):
            acc_lines.append(line)

        elif len(acc_lines) and not line:
            new_ndfa = NDFA.from_grammar(acc_lines)
            ndfa.add_grammar(new_ndfa.states)
            
            acc_lines = []

        if line and NDFA.is_sentence(line):
            new_ndfa = NDFA.from_token(line)
            ndfa.add_grammar(new_ndfa.states)

    if len(acc_lines):
        new_ndfa = NDFA.from_grammar(acc_lines)
        ndfa.add_grammar(new_ndfa.states)

    return ndfa

ndfa = generate_ndfa(get_inputs())

print("### NDFA ###")
print(ndfa.asci_table())

print()
print("### DFA ###")
dfa = DFA.from_NDFA(ndfa)
print(dfa.asci_table())
