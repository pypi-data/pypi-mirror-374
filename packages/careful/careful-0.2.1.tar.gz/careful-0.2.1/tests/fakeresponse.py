class FakeResponse:
    def __init__(
        self,
        url: str,
        code: int,
        content: str | bytes,
        encoding: str = "utf-8",
        headers: dict | None = None,
    ):
        self.url = url
        self.status_code = code
        self.content = content
        self.text = str(content)
        self.encoding = encoding
        self.headers = headers or {}
