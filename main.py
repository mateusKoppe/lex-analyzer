import re
from models import Expression, Token

def get_inputs() -> list:
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return lines


def generate_raw(raw: str) -> Expression:
    match = re.search(Expression.regex, raw)
    
    if match:
        return Expression(raw)
    else:
        return Token(raw)


def convert_objects(lines: list) -> list:
    objects = []
    for line in lines:
        objects.append(generate_raw(line))
    return objects

objects = convert_objects(get_inputs())

print("noice")

