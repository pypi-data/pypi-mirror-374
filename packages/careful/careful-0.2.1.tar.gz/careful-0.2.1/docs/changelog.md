# Changelog

## 0.2.0 - 6 September 2025

- Initial release, mostly a port of `scrapelib` functionality.

## scrapelib

The original version of this library is a port of `scrapelib` (2.4.1).

Changes from this version were to:

- use `httpx` instead of `requests`
- dropped quite a few unnecessary features that were mainly in `scrapelib` for backwards-compatability reasons.
- use a composable interface instead of the inheritance-based one from `scrapelib`, aiming at making future enhancements/porting easier.

This library is a partial rewrite of [scrapelib](https://pypi.org/project/scrapelib/).
Thanks to all of [scrapelib's original contributors](https://github.com/jamesturk/scrapelib/graphs/contributors) and users.

`scrapelib` originally wrapped `urllib2`, eventually migrating to `requests`.

There are a few things that scrapelib did that this doesn't:

- support FTP requests via HTTP-like API
- extend the client with a `urlretrieve` function
- provide helpers for working with headers, timeouts, and custom ciphers

The first two are possible but didn't seem necessary at the moment.
The latter was very `requests`-specific, and so hasn't been replicated here.
