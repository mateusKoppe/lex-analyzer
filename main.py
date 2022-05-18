from finite_automaton.nfa import NFA
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


def generate_nfa(lines):
    nfa = NFA.from_token(lines[0])
    del lines[0]
    acc_lines = []
    for line in lines:
        if NFA.is_expression(line):
            acc_lines.append(line)

        elif len(acc_lines) and not line:
            new_nfa = NFA.from_grammar(acc_lines)
            nfa.concat(new_nfa)
            
            acc_lines = []

        if line and NFA.is_sentence(line):
            new_nfa = NFA.from_token(line)
            nfa.concat(new_nfa)

    if len(acc_lines):
        new_nfa = NFA.from_grammar(acc_lines)
        nfa.concat(new_nfa)

    return nfa

nfa = generate_nfa(get_inputs())

print("### NFA ###")
print(nfa.asci_table())

# print()
# print("### DFA ###")
# dfa = DFA.from_NFA(nfa)
# print(dfa.asci_table())
