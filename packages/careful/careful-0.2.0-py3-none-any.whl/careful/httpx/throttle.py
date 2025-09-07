import time
import types
import functools
import logging
from httpx import Client

log = logging.getLogger("httpx")


def _throttle_request(client: Client, *args, **kwargs):
    now = time.time()
    diff = client._request_frequency - (now - client._last_request)
    if diff > 0:
        log.debug("throttled, sleeping for %fs", diff)
        time.sleep(diff)
        client._last_request = time.time()
    else:
        client._last_request = now
    return client._no_throttle_request(*args, **kwargs)


def make_throttled_client(
    *,
    client: Client | None = None,
    requests_per_minute: float = 0,
):
    if requests_per_minute <= 0:
        raise ValueError("requests per minute must be a positive number")

    if client is None:
        client = Client()

    client._last_request = 0.0
    client._requests_per_minute = requests_per_minute
    client._request_frequency = 60.0 / requests_per_minute

    client._no_throttle_request = client.request
    client.request = types.MethodType(
        functools.wraps(client.request)(_throttle_request), client
    )
    return client
