from httpx import Response
from typing import Callable

ResponsePredicate = Callable[[Response], bool]

CacheKeyfunc = Callable[[str,str,dict], str]
