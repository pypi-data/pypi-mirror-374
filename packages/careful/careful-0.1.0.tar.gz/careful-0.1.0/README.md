**careful_httpx** is a library for making requests to less-than-reliable websites.

It is based on [scrapelib](https://pypi.org/scrapelib/), which has powered Open States & many other Python scrapers for over 15 years.

Code: <https://codeberg.org/jpt/careful_httpx>

Documentation: TODO

## Features

Enhances [`httpx.Client`](https://www.python-httpx.org) with features useful for writing long-running scrapers & crawlers, particularly against sites that are slow or have intermittent errors.

- retries
- throttling
- dev-cache for iterating on scrapers

### example

TODO

### features this has that scrapelib doesn't

- httpx support
- composable interface, can augment Client with just the enhancements you want

TODO: don't allow instantiating bad patch classes, and check for incompatible configs

### features scrapelib had that this doesn't

Open to considering if there is interest, but didn't seem necessary.

- HTTP(S) and FTP requests via an identical API
- allow setting custom ciphers
- have urlretrieve
- support FTP
- set custom user-agent/mess w/ headers
