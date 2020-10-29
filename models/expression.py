import re
from .production import Production

class Expression():
    name: str
    productions: []
    raw: str

    regex = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z])>)*([a-zε]*)\s*\|?)+)$"

    def __init__(self, raw: str):
        self.raw = raw
        self.value = raw

        groups = re.search(Expression.regex, self.raw).groups()
        self.name = groups[0]
        self.productions = Expression.get_productions(groups[1])

    def __str__(self):
        return f"<Expression {self.raw}>"

    @staticmethod
    def get_productions(raw: str) -> list:
        productions_raw = raw.split("|")
        productions = []
        for production_raw in productions_raw:
            production = Production(production_raw)
            productions.append(production)

        return productions