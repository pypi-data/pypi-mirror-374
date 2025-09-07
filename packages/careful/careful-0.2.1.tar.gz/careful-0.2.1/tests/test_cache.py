from pytest_httpbin.serve import Server  # type: ignore
from httpx import Response
from careful.httpx import make_dev_caching_client, MemoryCache, FileCache, SqliteCache


def test_dev_caching(httpbin: Server) -> None:
    client = make_dev_caching_client(cache_storage=MemoryCache(), write_only=False)

    resp = client.get(httpbin.url + "/status/200")
    assert not resp.fromcache
    resp = client.get(httpbin.url + "/status/200")
    assert resp.fromcache


def test_dev_caching_params(httpbin: Server) -> None:
    client = make_dev_caching_client(cache_storage=MemoryCache(), write_only=False)

    resp = client.get(httpbin.url + "/status/200?a=1&b=2")
    assert not resp.fromcache
    resp = client.get(httpbin.url + "/status/200?a=1&b=2")
    assert resp.fromcache
    resp = client.get(httpbin.url + "/status/200?a=1&b=3")
    assert not resp.fromcache


# test storages #####


def _test_cache_storage(storage_obj) -> None:
    # unknown key returns None
    assert storage_obj.get("one") is None

    _content_as_bytes = b"here's unicode: \xe2\x98\x83"
    _content_as_unicode = "here's unicode: \u2603"

    # set 'one'
    resp = Response(200)
    resp.headers["x-num"] = "one"
    resp._content = _content_as_bytes
    storage_obj.set("one", resp)
    cached_resp = storage_obj.get("one")
    assert cached_resp is not None
    if cached_resp is not None:
        assert cached_resp.headers["x-num"] == "one"
        assert cached_resp.status_code == 200
        cached_resp.encoding = "utf8"
        assert cached_resp.text == _content_as_unicode


def test_memory_cache() -> None:
    _test_cache_storage(MemoryCache())


def test_file_cache() -> None:
    fc = FileCache("cache")
    fc.clear()
    _test_cache_storage(fc)
    fc.clear()


def test_sqlite_cache() -> None:
    sc = SqliteCache("cache.db")
    sc.clear()
    _test_cache_storage(sc)
    sc.clear()
