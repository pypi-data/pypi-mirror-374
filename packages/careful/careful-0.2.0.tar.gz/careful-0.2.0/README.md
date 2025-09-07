# careful

<img src="/carefully-3681327.svg" width=100 height=100 alt="logo of a warning sign">

**careful** is a library for making requests to unreliable websites with httpx.

**Code**: <https://codeberg.org/jpt/careful>

**Docs**: <https://careful.jpt.sh>

It offers enhancements to 
[`httpx.Client`](https://www.python-httpx.org)
useful for writing long-running scrapers & crawlers, particularly against sites that are slow or have intermittent errors.

- **configurable retry support.** retry on timeouts or other errors, with exponential back-off.
- **simple request throttling.** set a maximum number of requests per minute.
- **development cache.** configurable caching aimed at reducing redundant requests made while authoring/testing web scrapers.

### example

```python
from httpx import Client
from careful.httpx import make_careful_client

client = make_careful_client(
    # can configure httpx.Client however you usually would
    client=Client(headers={'user-agent': 'careful/1.0'}),
    # retries are configurable w/ exponential back off
    retry_attempts=2,
    retry_wait_seconds=5,
    # can cache to process memory, filesystem, or SQLite
    cache_storage=MemoryCache(),
    # requests will automatically be throttled to aim at this rate
    requests_per_minute=60,
)

# all normal methods on httpx.Client make use of configured enhancements
client.get("https://example.com")
```


---

Logo licensed from [Adrien Coquet via Noun Project](https://thenounproject.com/icon/carefully-3681327/)
