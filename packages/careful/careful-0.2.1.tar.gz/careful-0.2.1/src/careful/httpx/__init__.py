from .retries import make_retry_client, retry_default_rule
from .throttle import make_throttled_client
from .dev_cache import (
    make_dev_caching_client,
    MemoryCache,
    FileCache,
    SqliteCache,
    CacheStorageBase,
    _cache_200s,
    _default_keyfunc,
)
from ._types import ResponsePredicate, CacheKeyfunc
from httpx import Client


def make_careful_client(
    *,
    client: Client | None = None,
    retry_attempts: int = 0,
    retry_wait_seconds: float = 10,
    should_retry: ResponsePredicate = retry_default_rule,
    requests_per_minute: int = 0,
    cache_storage: CacheStorageBase = None,
    cache_write_only: bool = False,
    should_cache: ResponsePredicate = _cache_200s,
    cache_keyfunc: CacheKeyfunc = _default_keyfunc,
):
    """
    This function patches an `httpx.Client` so that all requests made with the client support
     [retries](#retries), [throttling](#throttling), and [development caching](#development-caching).


    Parameters:
        client: A pre-configured `httpx.Client`. If omitted a default client will be created.

        retry_attempts: Maximum number of retries. If non-zero will retry up to this many times
                         with increasing wait times, starting with `retry_wait_seconds`.

        retry_wait_seconds: Number of seconds to sleep between first attempt and first retry.
                             Subsequent attempts will increase exponentially (2x, 4x, 8x, etc.)

        should_retry: Predicate function that takes a `httpx.Response` and returns `True` if it should be retried.

        requests_per_minute: Maximum number of requests per minute. (e.g. 30 will throttle to ~2s between requests)

        cache_storage: An object that implements the [cache storage interface](#cache-storage).

        cache_write_only: Update cache, but never read from it.

        should_cache: Predicate function that takes a `httpx.Response` and returns `True` if it should be cached.

        cache_keyfunc: Function that takes request details and returns a unique cache key.

    ## Retries

    If `retry_attempts` is set, responses will be passed to `should_retry`.
    Responses that are rejected (return `True`) will be retried after a wait based on
    `retry_wait_seconds`.
    Each retry will wait twice as long as the one before.

    ## Throttling

    If `requests_per_minute` is set, standard (non-retry) requests will automatically
    sleep for a short period to target the given rate.

    For example, at 30rpm, the sleep time on a fast request will be close to 2 seconds.

    ## Development Caching

    Why **development caching?**

    This feature is named as a reminder that **this is not true HTTP caching**, which
    should take various headers into account. Look at libraries like [hishel](https://hishel.com) if that's what you are after.

    The purpose of this feature is to allow you to cache all of your HTTP requests during development.
    Often when writing a scraper or crawler, you wind up hitting the site you are working on more often than you'd like-- each time you iterate on your code you're likely making redundant requests to pages that haven't changed.

    By caching all successful requests (configurable with the `should_cache` parameter),
    you can easily re-run scrapers without making redundant HTTP requests.
    This means faster development time & happier upstream servers.

    To enable development caching, assign a [`MemoryCache`][careful.httpx.MemoryCache],
    [`FileCache`][careful.httpx.FileCache], or [`SqliteCache`][careful.httpx.SqliteCache] to
    the `cache_storage` property of a `scrapelib.Scraper`.

    ---

    When multiple features are applied, the order of wrapping ensures that:
       - the cache is checked first, and bypasses throttling if hit
       - retries use their own delays, but not throttled separately
    """
    if client is None:
        client = Client()
    # order matters, retry on inside b/c it is last-chance scenario
    if retry_attempts:
        client = make_retry_client(
            client=client,
            attempts=retry_attempts,
            wait_seconds=retry_wait_seconds,
            should_retry=should_retry,
        )
    # throttling around retries
    if requests_per_minute:
        client = make_throttled_client(
            client=client, requests_per_minute=requests_per_minute
        )
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
    "SqliteCache",
]
