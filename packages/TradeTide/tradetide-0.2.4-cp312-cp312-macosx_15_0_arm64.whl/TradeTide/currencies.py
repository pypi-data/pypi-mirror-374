# currencies.py
from enum import Enum

class Currency(Enum):
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    NZD = "NZD"  # New Zealand Dollar
    SEK = "SEK"  # Swedish Krona
    MXN = "MXN"  # Mexican Peso
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    NOK = "NOK"  # Norwegian Krone
    KRW = "KRW"  # South Korean Won
    TRY = "TRY"  # Turkish Lira
    INR = "INR"  # Indian Rupee
    RUB = "RUB"  # Russian Ruble
    ZAR = "ZAR"  # South African Rand
    BRL = "BRL"  # Brazilian Real
    # …add more as needed…

    @classmethod
    def list(cls):
        """Return all currency codes as a list of strings."""
        return [c.value for c in cls]
