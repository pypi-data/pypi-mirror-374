import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    Optional,
    ParamSpec,
    Sequence,
    TypeVar,
    overload,
)

import httpx
from rich import print

SetClient = Callable[[], httpx.AsyncClient]


async def _log_response(res: httpx.Response) -> None:
    print(f"[http] {res.request.method} {res.request.url} -> {res.status_code}")


_client_override: ContextVar[Optional[httpx.AsyncClient]] = ContextVar(
    "httpx_client_override", default=None
)


def _default_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
        event_hooks={
            "response": [_log_response],
        },
    )


def get_client() -> httpx.AsyncClient:
    """Return the current context-scoped HTTP client.

    Requires being inside `lifespan()` or having set an override explicitly.
    Raises a RuntimeError if called outside a managed context to avoid leaking
    a global client that callers might forget to close.
    """
    override = _client_override.get()
    if override is None:
        raise RuntimeError(
            "No HTTP client found in context. Wrap your call in `async with "
            "lifespan(): ...` or decorate your click command with "
            "`@run_in_lifespan`."
        )
    return override


async def request(
    url: str,
    *,
    method: str = "GET",
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    data: Any | None = None,
    raise_on_status_except_for: Sequence[int] | None = None,
) -> httpx.Response:
    resp = await get_client().request(
        method, url, headers=headers, params=params, json=json, data=data
    )
    if not resp.is_success and resp.status_code not in set(
        raise_on_status_except_for or []
    ):
        resp.raise_for_status()
    return resp


@asynccontextmanager
async def lifespan(
    *, set_client: Optional[SetClient] = None
) -> AsyncIterator[httpx.AsyncClient]:
    """Provide a per-context client set in a ContextVar and close on exit.

    Useful for tests or wrapping a whole command without relying on globals.
    """
    client = set_client() if set_client is not None else _default_client()
    token = _client_override.set(client)
    try:
        yield client
    finally:
        _client_override.reset(token)
        await client.aclose()


T = TypeVar("T")
P = ParamSpec("P")


@overload
def run_in_lifespan(func: Callable[P, Awaitable[T]]) -> Callable[P, T]: ...


@overload
def run_in_lifespan(
    *, set_client: Optional[SetClient] = ...
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, T]]: ...


def run_in_lifespan(
    func: Optional[Callable[P, Awaitable[T]]] = None,
    *,
    set_client: Optional[SetClient] = None,
):
    """Decorator to run an async function inside a managed httpx lifespan.

    Can be used bare as ``@run_in_lifespan`` or configured with a client factory
    function: ``@run_in_lifespan(set_client=lambda: httpx.AsyncClient(...))``.
    """

    def decorator(f: Callable[P, Awaitable[T]]) -> Callable[P, T]:
        @wraps(f)
        def _runner(*args: P.args, **kwargs: P.kwargs) -> T:
            async def _wrap() -> T:
                async with lifespan(set_client=set_client):
                    return await f(*args, **kwargs)

            return asyncio.run(_wrap())

        return _runner

    if func is None:
        return decorator
    else:
        return decorator(func)
