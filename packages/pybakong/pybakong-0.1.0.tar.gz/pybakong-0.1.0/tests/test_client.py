
import pytest
from pybakong import BakongClient, BakongAPIError

def test_client_init():
    client = BakongClient()
    assert client.base_url == "https://api-bakong.nbc.gov.kh/v1"
    assert client.token is None
