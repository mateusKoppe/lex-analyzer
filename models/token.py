class Token():
    value: str

    def __init__(self, raw: str):
        self.value = raw

    def __str__(self):
        return f"<Token {self.value}>"