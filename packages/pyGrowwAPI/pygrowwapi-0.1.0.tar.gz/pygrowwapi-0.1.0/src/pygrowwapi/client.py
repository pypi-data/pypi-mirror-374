from __future__ import annotations

import requests
from datetime import datetime, timedelta
from .model import Candle


class GrowwClient:
    """
    Client for fetching stock data from Groww's unofficial API.
    Provides both live quotes and historical OHLCV data.
    """

    BASE_URL: str = "https://groww.in/v1/api"
    QUOTES_URL: str = BASE_URL + "/stocks_data/v1/accord_points/exchange/NSE/segment/CASH/latest_prices_ohlc/{symbol}"
    HISTORY_URL: str = BASE_URL + "/charting_service/v2/chart/exchange/NSE/segment/CASH/{symbol}"

    def __init__(self, symbol: str) -> None:
        """
        Initialize the Groww client.

        Args:
            symbol (str): Stock symbol (e.g., "SBIN", "TCS").
        """
        self.symbol = symbol.upper()

    def get_quotes(self) -> dict:
        """
        Fetch the latest OHLC quotes for the stock.

        Returns:
            dict: JSON response from Groww API with latest prices.
        """
        url = self.QUOTES_URL.format(symbol=self.symbol)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def history_price(self, range_period: str, interval: str) -> list[Candle]:
        """
        Fetch historical OHLCV candle data for the stock.

        Args:
            starting_period (str): Period like "30day", "2week", "6month", "5year".
            interval (str): Interval like "1min", "15min", "1day", "1week".

        Returns:
            list[Candle]: List of Candle objects.
        """
        # Convert period → start/end timestamps
        period_value, period_unit = self._parse_period(range_period)
        days = period_value * {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
        }[period_unit]

        now = datetime.now()
        start_date = now - timedelta(days=days)
        params = {
            "startTimeInMillis": int(start_date.timestamp() * 1000),
            "endTimeInMillis": int(now.timestamp() * 1000),
            "intervalInMinutes": self._parse_interval(interval),
        }

        # Fetch candles
        url = self.HISTORY_URL.format(symbol=self.symbol)
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        raw_candles = resp.json().get("candles", [])

        return [Candle.from_raw(c) for c in raw_candles]

    def _parse_period(self, period: str) -> tuple[int, str]:
        """
        Parse period string into (value, unit).
        Example: "30day" → (30, "day")

        Args:
            period (str): Period string.

        Returns:
            tuple[int, str]: (value, unit)
        """
        for unit in ("day", "week", "month", "year"):
            if unit in period:
                return int(period.replace(unit, "")), unit
        raise ValueError(f"Invalid period format: {period}")

    def _parse_interval(self, interval: str) -> int:
        """
        Convert interval string into minutes.
        Example: "1day" → 1440

        Args:
            interval (str): Interval string.

        Returns:
            int: Interval in minutes.
        """
        mapping = {
            "min": 1,
            "hour": 60,
            "day": 1440,
            "week": 1440 * 7,
            "month": 1440 * 30,
            "year": 1440 * 365,
        }
        for unit, factor in mapping.items():
            if unit in interval:
                return int(interval.replace(unit, "")) * factor
        raise ValueError(f"Invalid interval format: {interval}")


