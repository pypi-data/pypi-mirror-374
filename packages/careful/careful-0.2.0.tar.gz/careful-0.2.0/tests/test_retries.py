from careful.httpx import make_retry_client
from careful.httpx.retries import retry_all_400s_500s
from unittest import mock
from fakeresponse import FakeResponse


def test_retry() -> None:
    client = make_retry_client(attempts=3, wait_seconds=0.001)

    # On the first call return a 500, then a 200
    mock_request = mock.Mock(
        side_effect=[
            FakeResponse("http://dummy/", 500, "failure!"),
            FakeResponse("http://dummy/", 200, "success!"),
        ]
    )

    with mock.patch.object(client, "send", mock_request):
        resp = client.get("http://dummy/")
    assert mock_request.call_count == 2

    # 500 always
    mock_request = mock.Mock(
        return_value=FakeResponse("http://dummy/", 500, "failure!")
    )

    with mock.patch.object(client, "send", mock_request):
        resp = client.get("http://dummy/")
    assert resp.status_code == 500
    assert mock_request.call_count == 4  # try four times


def test_retry_404() -> None:
    client = make_retry_client(attempts=3, wait_seconds=0.001, should_retry=retry_all_400s_500s)

    # On the first call return a 404, then a 200
    mock_request = mock.Mock(
        side_effect=[
            FakeResponse("http://dummy/", 404, "failure!"),
            FakeResponse("http://dummy/", 200, "success!"),
        ]
    )

    with mock.patch.object(client, "send", mock_request):
        resp = client.get("http://dummy/")  # type: ignore
    assert mock_request.call_count == 2
    assert resp.status_code == 200

    # 404 always
    mock_request = mock.Mock(
        return_value=FakeResponse("http://dummy/", 404, "failure!")
    )

    # four tries
    with mock.patch.object(client, "send", mock_request):
        resp = client.get("http://dummy/")
    assert resp.status_code == 404
    assert mock_request.call_count == 4
    assert resp.status_code == 404


def test_no_retry_404() -> None:
    client = make_retry_client(attempts=3, wait_seconds=0.001)

    # On the first call return a 404, then a 200
    mock_request = mock.Mock(
        side_effect=[
            FakeResponse("http://dummy/", 404, "failure!"),
            FakeResponse("http://dummy/", 200, "success!"),
        ]
    )

    with mock.patch.object(client, "send", mock_request):
        resp = client.get("http://dummy/")  # type: ignore
    assert mock_request.call_count == 1
    assert resp.status_code == 404


# def test_retry_ssl() -> None:
#     s = make_retry_client(retry_attempts=5, retry_wait_seconds=0.001, raise_errors=False)

#     # ensure SSLError is considered fatal even w/ retries
#     with mock.patch.object(requests.Session, "request", mock_sslerror):
#         with pytest.raises(requests.exceptions.SSLError):
#             s.get("http://dummy/", retry_on_404=True)  # type: ignore
#     assert mock_sslerror.call_count == 1
