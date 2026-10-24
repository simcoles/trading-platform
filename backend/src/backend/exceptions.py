class UnknownSymbolError(Exception):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Symbol {symbol} not found")
