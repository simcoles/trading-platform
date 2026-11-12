from decimal import Decimal


class TradingRuleError(Exception):
    """An order that breaks a trading rule. The API returns 409 for all of these."""


class InsufficientCashError(TradingRuleError):
    def __init__(self, cost: Decimal, available: Decimal):
        self.cost = cost
        self.available = available
        super().__init__(
            f"Insufficient cash: order costs {cost} but only {available} is available"
        )


class InsufficientSharesError(TradingRuleError):
    def __init__(self, symbol: str, quantity: int, held: int):
        self.symbol = symbol
        self.quantity = quantity
        self.held = held
        super().__init__(
            f"Insufficient shares: cannot sell {quantity} {symbol}, only {held} held"
        )


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
