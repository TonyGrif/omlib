"""Python wrapper around various Open-Meteo APIs."""

from omlib.client import Client
from omlib.historic import HistoricAPI

__all__ = ["Client", "HistoricAPI"]
