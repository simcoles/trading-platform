class UnknownSymbolError(Exception):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Symbol {symbol} not found")


class SymbolAlreadyInWatchlistError(Exception):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Symbol {symbol} is already in the watchlist")


class SymbolNotInWatchlistError(Exception):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Symbol {symbol} is not in the watchlist")
