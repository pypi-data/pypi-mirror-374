import time
import types
import functools
import logging
from httpx import Client, Response, HTTPError

log = logging.getLogger("httpx")


def retry_default_rule(response: Response) -> bool:
    # default behavior is to retry 400s and 500s but not 404s
    return response.status_code >= 400 and response.status_code != 404


def retry_only_500s(response: Response) -> bool:
    return response.status_code >= 500


def retry_all_400s_500s(response: Response) -> bool:
    return response.status_code >= 400


def _retry_request(client: Client, *args, **kwargs):
    # the retry loop
    tries = 0
    exception_raised = None

    while tries <= client._retry_attempts:
        exception_raised = None

        try:
            tries += 1
            resp = client._no_retry_request(*args, **kwargs)

            # break from loop on an accepted response
            if not client._should_retry(resp):
                break

        except HTTPError as e:
            exception_raised = e

            if exception_response := getattr(e, "response", None):
                if not client._should_retry(exception_response):
                    break

        # if we're going to retry, sleep first
        if tries <= client._retry_attempts:
            # twice as long each time
            wait = client._retry_wait_seconds * (2 ** (tries - 1))
            if exception_raised:
                log.info(
                    "exception %s, sleeping for %s seconds before retry #%s",
                    exception_raised,
                    wait,
                    tries,
                )
            else:
                log.info(
                    "response %s, sleeping for %s seconds before retry #%s",
                    resp,
                    wait,
                    tries,
                )
            time.sleep(wait)

    # out of the loop, either an exception was raised or we had a success
    if exception_raised:
        raise exception_raised
    return resp


def make_retry_client(
    *,
    client: Client | None = None,
    attempts: int = 1,
    wait_seconds: float = 10,
    should_retry=retry_default_rule,
):
    if client is None:
        client = Client()
    client._retry_attempts = max(0, attempts)
    client._retry_wait_seconds = wait_seconds
    client._should_retry = should_retry

    client._no_retry_request = client.request
    client.request = types.MethodType(
        functools.wraps(client.request)(_retry_request), client
    )

    return client
