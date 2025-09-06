import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    overload,
)

import aiohttp
from tqdm.asyncio import tqdm
from yarl import URL

ItemT = TypeVar("ItemT", int, str)
ResultT = TypeVar("ResultT")

# A JSON value returned by `resp.json()`
JSONValue = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]

# Supported HTTP methods
HTTPMethod = Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "CONNECT",
]

_RETRY_STATUSES: set[int] = {429, 500, 502, 503, 504}

__all__ = [
    "iter_requests",
    "request",
]


# -------------------------
# Internal helper functions
# -------------------------


def _resolve_timeout(
    timeout: Optional[aiohttp.ClientTimeout | float], *, default_total: float = 60.0
) -> aiohttp.ClientTimeout:
    if isinstance(timeout, (int, float)):
        return aiohttp.ClientTimeout(total=float(timeout))
    if isinstance(timeout, aiohttp.ClientTimeout):
        return timeout
    return aiohttp.ClientTimeout(total=default_total)


def _get_retry_statuses(
    retry_statuses: Optional[Sequence[int] | set[int]],
) -> set[int]:
    return set(retry_statuses) if retry_statuses is not None else _RETRY_STATUSES


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
            return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
        except Exception:
            return None


def _backoff_delay(attempt: int, base: float, maximum: float) -> float:
    return min(base * (2**attempt), maximum)


async def _consume_and_release(resp: aiohttp.ClientResponse) -> None:
    try:
        await resp.read()
    finally:
        resp.release()


@asynccontextmanager
async def _ensure_session(
    session: Optional[aiohttp.ClientSession],
    *,
    timeout: Optional[aiohttp.ClientTimeout | float],
    max_concurrency: int,
):
    """Yield a session and close it on exit if we created it."""
    if session is None:
        created = True
        effective_timeout = _resolve_timeout(timeout)
        session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=max_concurrency),
            timeout=effective_timeout,
        )
    else:
        created = False
    try:
        yield session
    finally:
        if created:
            await session.close()


async def _retry_loop(
    make_response: Callable[[], Awaitable[aiohttp.ClientResponse]],
    *,
    retries: int,
    retry_statuses: set[int],
    retry_backoff_base: float,
    retry_backoff_max: float,
) -> aiohttp.ClientResponse:
    """Execute an async request factory with retry/backoff rules.

    Retries on:
    - Response status in `retry_statuses` (honors Retry-After when present)
    - aiohttp.ClientError / asyncio.TimeoutError exceptions
    """
    attempt = 0
    while True:
        try:
            resp = await make_response()

            if resp.status in retry_statuses and attempt < retries:
                delay_hdr = resp.headers.get("Retry-After")
                override = _parse_retry_after(delay_hdr)
                sleep_for = (
                    float(override)
                    if override is not None
                    else _backoff_delay(attempt, retry_backoff_base, retry_backoff_max)
                )
                await _consume_and_release(resp)
                attempt += 1
                await asyncio.sleep(sleep_for)
                continue

            resp.raise_for_status()
            return resp
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if attempt < retries:
                sleep_for = _backoff_delay(
                    attempt, retry_backoff_base, retry_backoff_max
                )
                attempt += 1
                await asyncio.sleep(sleep_for)
                continue
            raise


# Overloads to constrain mutually exclusive parameters.
# Rules:
# - If `on_error` is provided, `raise_on_error` must be False.
# - If `raise_on_error` is True, `on_error` must be None.


@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: None = ...,
    on_error: Callable[[ItemT, BaseException], Awaitable[None]],
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: None = ...,
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


# base_url mode, no on_result, raise_on_error=True
@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[True],
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    on_result: None = ...,
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: None = ...,
    on_error: Callable[[ItemT, BaseException], Awaitable[None]],
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: None = ...,
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


# request_fn mode, no on_result, raise_on_error=True
@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[True],
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    on_result: None = ...,
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, JSONValue]]: ...


@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: Callable[[ItemT, BaseException], Awaitable[None]],
) -> AsyncIterator[tuple[ItemT, ResultT | BaseException]]: ...


@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, ResultT | BaseException]]: ...


# base_url mode, with on_result, raise_on_error=True
@overload
def iter_requests(
    *,
    base_url: str,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[True],
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: None = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, ResultT]]: ...


@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: Callable[[ItemT, BaseException], Awaitable[None]],
) -> AsyncIterator[tuple[ItemT, ResultT | BaseException]]: ...


@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, ResultT | BaseException]]: ...


# request_fn mode, with on_result, raise_on_error=True
@overload
def iter_requests(
    *,
    base_url: None = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    pbar: bool | str = ...,
    raise_on_error: Literal[True],
    method: HTTPMethod = "GET",
    headers: None = None,
    params: None = None,
    request_fn: Callable[
        [aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]
    ],
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    on_result: Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]],
    on_error: None = ...,
) -> AsyncIterator[tuple[ItemT, ResultT]]: ...


async def iter_requests(
    *,
    base_url: Optional[str] = None,
    max_concurrency: int = 32,
    items: Iterable[ItemT],
    session: Optional[aiohttp.ClientSession] = None,
    timeout: Optional[aiohttp.ClientTimeout | float] = None,
    pbar: bool | str = False,
    raise_on_error: bool = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    request_fn: Optional[
        Callable[[aiohttp.ClientSession, ItemT], Awaitable[aiohttp.ClientResponse]]
    ] = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Optional[Sequence[int] | set[int]] = None,
    on_result: Optional[
        Callable[[ItemT, aiohttp.ClientResponse], Awaitable[ResultT]]
    ] = None,
    on_error: Optional[Callable[[ItemT, BaseException], Awaitable[None]]] = None,
) -> AsyncIterator[tuple[ItemT, JSONValue | ResultT | BaseException]]:
    """Iterate `(item, result)` built from `base_url` or `request_fn`.

    - Concurrency is enforced via both a worker pool and
      `aiohttp.TCPConnector(limit=max_concurrency)` for owned sessions.
    - If `session` is None, an internal session is created with a default
      `ClientTimeout(total=60)`; a float `timeout` becomes `ClientTimeout(total=timeout)`.
    - Progress bar: set `pbar=True` to enable with no description or pass a
      string to use as the description.
    - Results are yielded in completion order.

    Error handling: When `raise_on_error=False` (default), request failures are yielded as
    Exception values; when `True`, failures are raised instead.

    Resource handling: Responses are closed on your behalf. If `on_result` is
    provided, its awaited return value is yielded for successes; on failure the
    Exception is yielded (or raised if `raise_on_error=True`). Without a
    callback, the parsed JSON body is yielded for successes; Exceptions are
    yielded or raised based on `raise_on_error`.
    """

    # Validate invalid input arrangements dynamically
    def _validate_inputs() -> None:
        if raise_on_error and on_error is not None:
            raise ValueError("on_error cannot be provided when raise_on_error=True")
        if (base_url is None) and (request_fn is None):
            raise ValueError("base_url must be provided unless request_fn is supplied")
        if (base_url is not None) and (request_fn is not None):
            raise ValueError("request_fn must be None when base_url is provided")

    _validate_inputs()

    if base_url is None:
        assert request_fn is not None, (
            "base_url must be provided unless request_fn is supplied"
        )
        base_url_obj: Optional[URL] = None
    else:
        base_url_obj = URL(base_url)
        # Normalize base path to avoid double slashes when appending segments
        if base_url_obj.path.endswith("/") and base_url_obj.path != "/":
            base_url_obj = base_url_obj.with_path(base_url_obj.path.rstrip("/"))

    async with _ensure_session(
        session, timeout=timeout, max_concurrency=max_concurrency
    ) as session:
        # Worker-pool scheduler: keep ≤ max_concurrency tasks in flight
        pending_tasks: set[
            asyncio.Task[
                tuple[ItemT, Optional[aiohttp.ClientResponse], Optional[BaseException]]
            ]
        ] = set()
        pbar_obj = None
        try:
            effective_retry_statuses = _get_retry_statuses(retry_statuses)

            async def fetch(
                item: ItemT,
            ) -> tuple[
                ItemT, Optional[aiohttp.ClientResponse], Optional[BaseException]
            ]:
                try:
                    if request_fn is not None:

                        async def op() -> aiohttp.ClientResponse:
                            return await request_fn(session, item)  # pyright: ignore[reportOptionalCall]
                    else:
                        assert base_url_obj is not None
                        assert method is not None, (
                            "method must be provided when using base_url"
                        )
                        url = base_url_obj / str(item)

                        async def op() -> aiohttp.ClientResponse:
                            return await session.request(
                                method, url, headers=headers, params=params
                            )

                    resp = await _retry_loop(
                        op,
                        retries=retries,
                        retry_statuses=effective_retry_statuses,
                        retry_backoff_base=retry_backoff_base,
                        retry_backoff_max=retry_backoff_max,
                    )
                    return item, resp, None
                except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                    if on_error is not None:
                        try:
                            await on_error(item, exc)
                        except Exception:
                            pass
                    return item, None, exc

            items_iter = iter(items)
            # Try to get a total for progress; fallback to indeterminate
            try:
                total = len(items)  # type: ignore[arg-type]
            except Exception:
                total = None

            if pbar:
                desc_str = pbar if isinstance(pbar, str) else None
                pbar_obj = tqdm(total=total, desc=desc_str)

            # Seed initial tasks
            for _ in range(max(1, max_concurrency)):
                try:
                    next_item = next(items_iter)
                except StopIteration:
                    break
                pending_tasks.add(asyncio.create_task(fetch(next_item)))

            while pending_tasks:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )
                for finished in done:
                    item, resp, err = await finished
                    if pbar_obj is not None:
                        pbar_obj.update(1)
                    if on_result is not None:
                        if resp is not None:
                            async with resp:
                                result = await on_result(item, resp)
                            yield item, result
                        else:
                            if raise_on_error and err is not None:
                                raise err
                            yield item, err
                    else:
                        if err is not None:
                            if raise_on_error:
                                raise err
                            else:
                                yield item, err
                                continue
                        assert resp is not None
                        async with resp:
                            data = await resp.json()
                        yield item, data
                    try:
                        next_item = next(items_iter)
                    except StopIteration:
                        continue
                    pending_tasks.add(asyncio.create_task(fetch(next_item)))
        finally:
            # Cancel any in-flight tasks if the consumer stops early
            if pending_tasks:
                for t in pending_tasks:
                    t.cancel()
                try:
                    await asyncio.gather(*pending_tasks, return_exceptions=True)
                except Exception:
                    pass
            if pbar_obj is not None:
                pbar_obj.close()


async def request(
    *,
    url: str,
    session: aiohttp.ClientSession,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Optional[Sequence[int] | set[int]] = None,
) -> aiohttp.ClientResponse:
    """Issue a single HTTP request and return the raw `ClientResponse`.

    - Requires a provided `session` so that the caller manages its lifecycle.
    - Retries on statuses in `retry_statuses` (default: 429, 500, 502, 503, 504) and on
      `aiohttp.ClientError` / `asyncio.TimeoutError` with exponential backoff. Respects
      `Retry-After` if present.
    - Raises exceptions on failure after retries.
    - Caller is responsible for consuming and closing the response, e.g.:
      `async with resp: data = await resp.json()`.
    """
    effective_retry_statuses = _get_retry_statuses(retry_statuses)

    async def op() -> aiohttp.ClientResponse:
        return await session.request(method, url, headers=headers, params=params)

    # Let exceptions bubble up; return a live response on success
    resp = await _retry_loop(
        op,
        retries=retries,
        retry_statuses=effective_retry_statuses,
        retry_backoff_base=retry_backoff_base,
        retry_backoff_max=retry_backoff_max,
    )
    return resp
