"""Tests for omlib.client.Client."""

from omlib.client import Client


def test_defaults() -> None:
    client = Client()

    assert client.timeout == 30
    assert client.retries == 3
    assert client.base_url is None
    assert client.kwargs == {}


def test_custom_values() -> None:
    client = Client(timeout=10, retries=1, base_url="http://localhost:8080")

    assert client.timeout == 10
    assert client.retries == 1
    assert client.base_url == "http://localhost:8080"


def test_extra_kwargs_stored() -> None:
    client = Client(verify=False, proxies={"http": "http://proxy:3128"})

    assert client.kwargs["verify"] is False
    assert client.kwargs["proxies"] == {"http": "http://proxy:3128"}
