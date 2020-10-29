import re

class Production():
    raw: str
    terminals: str
    nonTerminals: str
    regex = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"

    def __init__(self, raw: str):
        groups = re.search(Production.regex, raw).groups()
        self.terminals = groups[0]
        self.nonTerminals = groups[2]
        print(self.terminals)
        print(self.nonTerminals)

    def __str__(self):
        return f"<Token {self.raw}>"