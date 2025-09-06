import time
import types
import functools
import logging
from httpx import Client, Response

log = logging.getLogger("httpx")


def _default_accept_response(response: Response) -> bool:
    return response.status_code < 400


def _retry_request(client: Client, *args, **kwargs):
    # the retry loop
    tries = 0
    exception_raised = None

    while tries <= client._retry_attempts:
        exception_raised = None

        try:
            resp = client._wrapped_request(*args, **kwargs)

            # break from loop on an accepted response
            if client._accept_response(resp) or (
                resp.status_code == 404 and not client._retry_on_404
            ):
                break

        except Exception as e:
            # TODO: exclude certain kinds of exceptions (SSL?) from retry
            exception_raised = e

            if exception_response := getattr(e, "response", None):
                if client._accept_response(exception_response):
                    break

        # if we're going to retry, sleep first
        tries += 1
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
    retry_on_404: bool = False,
    accept_response=_default_accept_response,
):
    if client is None:
        client = Client()
    client._retry_attempts = max(0, attempts)
    client._retry_wait_seconds = wait_seconds
    client._retry_on_404 = retry_on_404
    client._accept_response = accept_response

    client._wrapped_request = client.request
    client.request = types.MethodType(
        functools.wraps(client.request)(_retry_request), client
    )

    return client

