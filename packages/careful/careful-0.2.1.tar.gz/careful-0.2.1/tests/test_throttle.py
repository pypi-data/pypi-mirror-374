from careful.httpx import make_throttled_client
from unittest import mock
from typing import Any
from httpx import Request
from fakeresponse import FakeResponse


def request_200(request: Request, *args: Any, **kwargs: Any) -> FakeResponse:
    return FakeResponse(request.url, 200, b"ok")


mock_200 = mock.Mock(wraps=request_200)


def test_request_throttling() -> None:
    client = make_throttled_client(requests_per_minute=30)

    mock_sleep = mock.Mock()

    # check that sleep is called on call 2 & 3
    with mock.patch("time.sleep", mock_sleep):
        with mock.patch.object(client, "send", mock_200):
            client.get("http://dummy/")
            client.get("http://dummy/")
            client.get("http://dummy/")
            assert mock_sleep.call_count == 2
            # should have slept for ~2 seconds to aim at 30 per min
            assert 1.8 <= mock_sleep.call_args[0][0] <= 2.2
