import abc
import types
import functools
import logging
import re
import os
import glob
import hashlib
import sqlite3
import json

from httpx import Client, Response, Request

log = logging.getLogger("httpx")


def _default_keyfunc(
    method: str,
    url: str,
    params: dict | None = None,
) -> str | None:
    """
    Return a cache key from a given set of request parameters.

    Default behavior is to return a complete URL for all GET
    requests, and None otherwise.
    """
    if method.lower() != "get":
        return None

    return Request(url=url, method=method, params=params).url


def _cache_200s(response: Response) -> bool:
    """
    Check if a given Response object should be cached.

    Default behavior is to only cache responses with a 200 status code.
    """
    return response.status_code == 200


def _cached_request(client: Client, *args, **kwargs):
    method, url = args
    request_key = client._cache_keyfunc(method, url, kwargs["params"])

    # check cache for response
    cached_resp = None
    if request_key and not client._write_only:
        cached_resp = client._cache_storage.get(request_key)

    if cached_resp:
        # resp = cast(CacheResponse, resp_maybe)
        log.info("using cached response request_key=%s", request_key)
        cached_resp.fromcache = True
        resp = cached_resp
    else:
        resp = client._no_cache_request(*args, **kwargs)
        # save to cache if request and response meet criteria
        log.debug("XX %s %s", request_key, client._should_cache(resp))
        if request_key and client._should_cache(resp):
            client._cache_storage.set(request_key, resp)
            log.info("caching response request_key=%s", request_key)
        resp.fromcache = False

    return resp


def make_dev_caching_client(
    *,
    client: Client | None = None,
    cache_storage=None,
    cache_keyfunc=_default_keyfunc,
    should_cache=_cache_200s,
    write_only=False,
):
    """
    Returns an enhanced `httpx.Client` where requests are saved to a
    specified cache.

    This is denoted as a "dev_cache" because it is not intended to be a true
    HTTP cache, respecting cache headers/etc. If you are looking for that
    behavior, there are httpx libraries for that explicit purpose.

    Instead, the purpose of this cache is to make it possible to test scrapers
    locally without making hundreds of redundant requests.

    The strategy is configurable via `cache_keyfunc` and `should_cache`.

    The default strategy is simple:
    cache all GET requests that result in 200s, with no expiry.

    This works well for the case where you have hundreds of pages to scrape
    and want to make scraper adjustments without repeatedly making hits.

    It should *NOT* be used in production without adjusting these rules.
    """
    if client is None:
        client = Client()

    client._cache_storage = cache_storage
    client._cache_keyfunc = cache_keyfunc
    client._should_cache = should_cache
    client._write_only = write_only

    client._no_cache_request = client.request
    client.request = types.MethodType(
        functools.wraps(client.request)(_cached_request), client
    )
    return client


class CacheStorageBase(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> None | Response:
        raise NotImplementedError()

    @abc.abstractmethod
    def set(self, key: str, response: Response) -> None:
        raise NotImplementedError()


class MemoryCache(CacheStorageBase):
    """
    In memory cache for request responses.

    Example:

        make_careful_client(
            cache_storage=MemoryCache(),
        )

    """

    def __init__(self) -> None:
        self.cache: dict[str, Response] = {}

    def get(self, key: str) -> None | Response:
        """Get cache entry for key, or return None."""
        return self.cache.get(key, None)

    def set(self, key: str, response: Response) -> None:
        """Set cache entry for key with contents of response."""
        self.cache[key] = response


class FileCache(CacheStorageBase):
    """
    File-based cache for request responses.

    Parameters:
        cache_dir: directory for storing responses

    Example:

        make_careful_client(
            cache_storage=FileCache("_httpcache/"),
        )

    """

    # TODO: restore?
    # check_last_modified:  set to True to compare last-modified
    #                       timestamp in cached response with value from HEAD request

    # file name escaping inspired by httplib2
    _prefix = re.compile(r"^\w+://")
    _illegal = re.compile(r"[?/:|]+")
    _header_re = re.compile(r"([-\w]+): (.*)")
    _maxlen = 200

    def _clean_key(self, key: str) -> str:
        # strip scheme
        md5 = hashlib.md5(key.encode("utf8")).hexdigest()
        key = self._prefix.sub("", key)
        key = self._illegal.sub(",", key)
        return ",".join((key[: self._maxlen], md5))

    def __init__(self, cache_dir: str, check_last_modified: bool = False):
        # normalize path
        self.cache_dir = os.path.join(os.getcwd(), cache_dir)
        self.check_last_modified = check_last_modified
        # create directory
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get(self, orig_key: str) -> None | Response:
        """Get cache entry for key, or return None."""
        key = self._clean_key(orig_key)
        path = os.path.join(self.cache_dir, key)
        resp_headers = {}

        try:
            with open(path, "rb") as f:
                # read lines one at a time
                while True:
                    line = f.readline().decode("utf8").strip("\r\n")
                    # set headers

                    # if self.check_last_modified and re.search(
                    #     "last-modified", line, flags=re.I
                    # ):
                    #     # line contains last modified header
                    #     head_resp = requests.head(orig_key)

                    #     try:
                    #         new_lm = head_resp.headers["last-modified"]
                    #         old_lm = line[line.find(":") + 1 :].strip()
                    #         if old_lm != new_lm:
                    #             # last modified timestamps don't match, need to download again
                    #             return None
                    #     except KeyError:
                    #         # no last modified header present, so redownload
                    #         return None

                    header = self._header_re.match(line)
                    if header:
                        resp_headers[header.group(1)] = header.group(2)
                    else:
                        break
                # everything left is the real content
                resp_content = f.read()

            # status & encoding will be in headers, but are faked
            # need to split spaces out of status to get code (e.g. '200 OK')
            resp = Response(
                status_code=int(resp_headers.pop("status").split(" ")[0]),
                content=resp_content,
                default_encoding=resp_headers.pop("encoding"),
                headers=resp_headers,
            )
            return resp
        except IOError:
            return None

    def set(self, key: str, response: Response) -> None:
        """Set cache entry for key with contents of response."""
        key = self._clean_key(key)
        path = os.path.join(self.cache_dir, key)

        with open(path, "wb") as f:
            status_str = "status: {0}\n".format(response.status_code)
            f.write(status_str.encode("utf8"))
            encoding_str = "encoding: {0}\n".format(response.encoding)
            f.write(encoding_str.encode("utf8"))
            for h, v in response.headers.items():
                # header: value\n
                f.write(h.encode("utf8"))
                f.write(b": ")
                f.write(v.encode("utf8"))
                f.write(b"\n")
            # one blank line
            f.write(b"\n")
            f.write(response.content)

    def clear(self) -> None:
        # only delete things that end w/ a md5, less dangerous this way
        cache_glob = "*," + ("[0-9a-f]" * 32)
        for fname in glob.glob(os.path.join(self.cache_dir, cache_glob)):
            os.remove(fname)


class SqliteCache(CacheStorageBase):
    """
    sqlite cache for request responses.

    Parameters:
        cache_path: path for SQLite database file

    Example:

        make_careful_client(
            cache_storage=SQLiteCache("_cache.db"),
        )
    """

    _columns = ["key", "status", "modified", "encoding", "data", "headers"]

    def __init__(self, cache_path: str, check_last_modified: bool = False):
        self.cache_path = cache_path
        self.check_last_modified = check_last_modified
        self._conn = sqlite3.connect(cache_path)
        self._conn.text_factory = str
        self._build_table()

    def _build_table(self) -> None:
        """Create table for storing request information and response."""
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS cache
                (key text UNIQUE, status integer, modified text,
                 encoding text, data blob, headers blob)"""
        )

    def set(self, key: str, response: Response) -> None:
        """Set cache entry for key with contents of response."""
        mod = response.headers.pop("last-modified", None)
        status = int(response.status_code)
        rec = (
            key,
            status,
            mod,
            response.encoding,
            response.content,
            json.dumps(dict(response.headers)),
        )
        with self._conn:
            self._conn.execute("DELETE FROM cache WHERE key=?", (key,))
            self._conn.execute("INSERT INTO cache VALUES (?,?,?,?,?,?)", rec)

    def get(self, key: str) -> None | Response:
        """Get cache entry for key, or return None."""
        query = self._conn.execute("SELECT * FROM cache WHERE key=?", (key,))
        rec = query.fetchone()
        if rec is None:
            return None
        rec = dict(zip(self._columns, rec))

        # TODO evaluate/remove?
        # if self.check_last_modified:
        #     if rec["modified"] is None:
        #         return None  # no last modified header present, so redownload

        #     head_resp = requests.head(key)
        #     new_lm = head_resp.headers.get("last-modified", None)
        #     if rec["modified"] != new_lm:
        #         return None

        resp = Response(
            rec["status"],
            content=rec["data"],
            default_encoding=rec["encoding"],
            headers=json.loads(rec["headers"]),
        )
        return resp

    def clear(self) -> None:
        """Remove all records from cache."""
        with self._conn:
            self._conn.execute("DELETE FROM cache")

    def __del__(self) -> None:
        self._conn.close()
