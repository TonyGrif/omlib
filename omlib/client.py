"""HTTP client configuration for Open-Meteo API requests."""

from __future__ import annotations

from typing import Any, Dict


class Client:
    """HTTP settings passed to the requests library."""

    def __init__(
        self,
        timeout: int = 30,
        retries: int = 3,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the Client with the given HTTP settings.

        Args:
            timeout: Request timeout in seconds. Defaults to 30.
            retries: Number of retry attempts on failures. Defaults to 3.
            base_url: Override the default base URL for all API calls. When ``None``
                each API class uses its own default. Defaults to None.
            **kwargs: Additional keyword arguments forwarded to every ``requests`` call
        """
        self.timeout = timeout
        self.retries = retries
        self.base_url = base_url
        self.kwargs: Dict[str, Any] = kwargs
