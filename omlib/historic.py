"""Wrapper around the Open-Meteo Historical Weather API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from omlib.client import Client


class HistoricAPI:
    """Wrapper around the Open-Meteo Historical Weather API.

    Attributes:
        archive: Fetch historical weather data from the `/v1/archive` endpoint.
    """

    _BASE_URL = "https://archive-api.open-meteo.com"

    def __init__(
        self,
        client: Client,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        *,
        timezone: Optional[str] = None,
        temperature_unit: Optional[str] = None,
        wind_speed_unit: Optional[str] = None,
        precipitation_unit: Optional[str] = None,
    ) -> None:
        """Initializes the HistoricAPI with a client and query parameters.

        Args:
            client: A configured Client instance supplying HTTP settings.
            latitude: Latitude of the location.
            longitude: Longitude of the location.
            start_date: Inclusive start date in YYYY-MM-DD format.
            end_date: Inclusive end date in YYYY-MM-DD format.
            timezone: Timezone string or "auto"
            temperature_unit: The temp unit, "celsius" (default) or "fahrenheit".
            wind_speed_unit: The wind speed unit "kmh" (default), "ms", "mph", or "kn".
            precipitation_unit: Precepitation unit "mm" (default) or "inch".
        """
        self._client = client
        self._base_url = client.base_url or self._BASE_URL
        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date
        self.timezone = timezone
        self.temperature_unit = temperature_unit
        self.wind_speed_unit = wind_speed_unit
        self.precipitation_unit = precipitation_unit

    def _session(self) -> requests.Session:
        """Builds a requests Session with retry logic from the client.

        Returns:
            A configured requests.Session.
        """
        session = requests.Session()
        retry = Retry(
            total=self._client.retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def archive(
        self,
        *,
        hourly: Optional[List[str]] = None,
        **kwargs: object,
    ) -> Dict:
        """Fetch historical weather data from the `/v1/archive` endpoint.

        Args:
            hourly: Hourly variable(s) names to retrieve.
            **kwargs: Any additional Open-Meteo parameters.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            requests.HTTPError: If the API returns a non-2xx status.
        """
        params: Dict[str, Any] = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

        for key, value in [
            ("hourly", hourly),
            ("timezone", self.timezone),
            ("temperature_unit", self.temperature_unit),
            ("wind_speed_unit", self.wind_speed_unit),
            ("precipitation_unit", self.precipitation_unit),
        ]:
            if value is not None:
                params[key] = ",".join(value) if isinstance(value, list) else value

        params.update(kwargs)

        url = f"{self._base_url}/v1/archive"
        session = self._session()
        try:
            response = session.get(
                url,
                params=params,
                timeout=self._client.timeout,
                **self._client.kwargs,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        finally:
            session.close()
