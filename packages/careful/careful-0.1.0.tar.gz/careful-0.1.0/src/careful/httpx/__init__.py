from .retries import make_retry_client, _default_accept_response
from .throttle import make_throttled_client
from .dev_cache import (
    make_dev_caching_client,
    MemoryCache,
    FileCache,
    SQLiteCache,
    _cache_200s,
    _default_keyfunc,
)
from httpx import Client


def make_careful_client(
    client: Client,
    *,
    retry_attempts: int = 0,
    retry_wait_seconds: float = 10,
    retry_on_404: bool = False,
    accept_response=_default_accept_response,
    requests_per_minute: int = 0,
    cache_storage=None,
    cache_write_only=False,
    should_cache=_cache_200s,
    cache_keyfunc=_default_keyfunc,
):
    # order matters, retry on inside b/c it is last-chance scenario
    if retry_attempts:
        client = make_retry_client(
            client=client,
            attempts=retry_attempts,
            wait_seconds=retry_wait_seconds,
            retry_on_404=retry_on_404,
            accept_response=accept_response,
        )
    # throttling around retries
    if requests_per_minute:
        client = make_throttled_client(client, requests_per_minute=requests_per_minute)
    # caching on top layer, so cache will be checked first
    if cache_storage:
        client = make_dev_caching_client(
            client=client,
            cache_storage=cache_storage,
            cache_keyfunc=cache_keyfunc,
            should_cache=should_cache,
            write_only=cache_write_only,
        )

    return client


__all__ = [
    "make_retry_client",
    "make_throttled_client",
    "make_dev_caching_client",
    "MemoryCache",
    "FileCache",
    "SQLiteCache",
]
