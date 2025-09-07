from careful.httpx import make_careful_client, MemoryCache
from unittest import mock
from fakeresponse import FakeResponse


def test_full_careful_client():
    client = make_careful_client(
        retry_attempts=3,
        retry_wait_seconds=0.00001,
        cache_storage=MemoryCache(),
        requests_per_minute=60,
    )

    # On the first call return a 500, then a 200, then a 500 again
    mock_send = mock.Mock(
        side_effect=[
            FakeResponse("http://dummy/", 500, "failure!"),
            FakeResponse("http://dummy/", 200, "success!"),
            FakeResponse("http://dummy/2", 404, "success!"),
        ]
    )

    mock_sleep = mock.Mock()

    # check that sleep is called
    with mock.patch("time.sleep", mock_sleep):
        with mock.patch.object(client, "send", mock_send):
            resp = client.get("http://dummy/")

            # demonstrates a retry
            assert mock_send.call_count == 2
            assert resp.status_code == 200
            # sleep called by retry, not by throttle yet
            assert mock_sleep.call_count == 1

            # demonstrates a cache (no new call)
            resp = client.get("http://dummy/")
            assert mock_send.call_count == 2
            assert resp.status_code == 200
            assert mock_sleep.call_count == 1

            # a new, throttled call (no retry)
            resp = client.get("http://dummy/2")
            assert mock_send.call_count == 3
            assert resp.status_code == 404
            # call was throttled
            assert mock_sleep.call_count == 2
