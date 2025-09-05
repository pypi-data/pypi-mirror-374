import asyncio
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
    "iter_responses",
    "request",
]


# Overloads to constrain mutually exclusive parameters.
# Rules:
# - If `on_error` is provided, `raise_on_error` must be False.
# - If `raise_on_error` is True, `on_error` must be None.


@overload
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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
def iter_responses(
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


async def iter_responses(
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

    if session is None:
        own_session = True
        if isinstance(timeout, (int, float)):
            effective_timeout = aiohttp.ClientTimeout(total=float(timeout))
        elif isinstance(timeout, aiohttp.ClientTimeout):
            effective_timeout = timeout
        else:
            effective_timeout = aiohttp.ClientTimeout(total=60)

        session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=max_concurrency),
            timeout=effective_timeout,
        )
    else:
        own_session = False

    # Worker-pool scheduler: keep ≤ max_concurrency tasks in flight
    pending_tasks: set[
        asyncio.Task[
            tuple[ItemT, Optional[aiohttp.ClientResponse], Optional[BaseException]]
        ]
    ] = set()
    pbar_obj = None
    try:
        effective_retry_statuses: set[int] = (
            set(retry_statuses) if retry_statuses is not None else _RETRY_STATUSES
        )

        async def fetch(
            item: ItemT,
        ) -> tuple[ItemT, Optional[aiohttp.ClientResponse], Optional[BaseException]]:
            attempt = 0
            while True:
                try:
                    if request_fn is not None:
                        resp = await request_fn(session, item)
                    else:
                        assert base_url_obj is not None
                        assert method is not None, (
                            "method must be provided when using base_url"
                        )
                        url = base_url_obj / str(item)
                        resp = await session.request(
                            method, url, headers=headers, params=params
                        )

                    # If status is retryable and we have attempts left, backoff
                    if resp.status in effective_retry_statuses and attempt < retries:
                        retry_after_hdr = resp.headers.get("Retry-After")
                        delay: Optional[float] = None
                        if retry_after_hdr:
                            try:
                                delay = float(retry_after_hdr)
                            except ValueError:
                                try:
                                    dt = parsedate_to_datetime(retry_after_hdr)
                                    delay = max(
                                        0.0,
                                        (
                                            dt - datetime.now(timezone.utc)
                                        ).total_seconds(),
                                    )
                                except Exception:
                                    delay = None

                        sleep_for: float = (
                            float(delay)
                            if delay is not None
                            else min(
                                retry_backoff_base * (2**attempt), retry_backoff_max
                            )
                        )
                        # Ensure connection is freed before sleeping/retrying
                        try:
                            await resp.read()
                        finally:
                            resp.release()
                        attempt += 1
                        await asyncio.sleep(sleep_for)
                        continue

                    resp.raise_for_status()
                    return item, resp, None
                except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                    if attempt < retries:
                        sleep_for: float = min(
                            retry_backoff_base * (2**attempt), retry_backoff_max
                        )
                        attempt += 1
                        await asyncio.sleep(sleep_for)
                        continue
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
        if own_session:
            await session.close()


@overload
async def request(
    *,
    url: str,
    max_concurrency: int = 32,
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    raise_on_error: Literal[False] = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
) -> JSONValue | BaseException: ...


@overload
async def request(
    *,
    url: str,
    max_concurrency: int = 32,
    session: Optional[aiohttp.ClientSession] = ...,
    timeout: Optional[aiohttp.ClientTimeout | float] = ...,
    raise_on_error: Literal[True],
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Sequence[int] | set[int] = ...,
) -> JSONValue: ...


async def request(
    *,
    url: str,
    max_concurrency: int = 32,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: Optional[aiohttp.ClientTimeout | float] = None,
    raise_on_error: bool = False,
    method: HTTPMethod = "GET",
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    retries: int = 2,
    retry_backoff_base: float = 0.5,
    retry_backoff_max: float = 5.0,
    retry_statuses: Optional[Sequence[int] | set[int]] = None,
) -> JSONValue | BaseException:
    """Issue a single HTTP request and return parsed JSON or an Exception.

    - If `session` is None, creates an internal session with `TCPConnector(limit=max_concurrency)`
      and a default `ClientTimeout(total=60)` (or converts a float into `ClientTimeout`).
    - Retries on statuses in `retry_statuses` (default: 429, 500, 502, 503, 504) and on
      `aiohttp.ClientError` / `asyncio.TimeoutError` with exponential backoff. Respects
      `Retry-After` if present.
    - On success, parses and returns JSON (`resp.json()`) and closes the response.
    - On failure, returns the Exception if `raise_on_error=False`; otherwise raises it.
    """
    if session is None:
        own_session = True
        if isinstance(timeout, (int, float)):
            effective_timeout = aiohttp.ClientTimeout(total=float(timeout))
        elif isinstance(timeout, aiohttp.ClientTimeout):
            effective_timeout = timeout
        else:
            effective_timeout = aiohttp.ClientTimeout(total=60)

        session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=max_concurrency),
            timeout=effective_timeout,
        )
    else:
        own_session = False

    effective_retry_statuses: set[int] = (
        set(retry_statuses) if retry_statuses is not None else _RETRY_STATUSES
    )

    try:
        attempt = 0
        while True:
            try:
                resp = await session.request(
                    method, url, headers=headers, params=params
                )

                if resp.status in effective_retry_statuses and attempt < retries:
                    retry_after_hdr = resp.headers.get("Retry-After")
                    delay: Optional[float] = None
                    if retry_after_hdr:
                        try:
                            delay = float(retry_after_hdr)
                        except ValueError:
                            try:
                                dt = parsedate_to_datetime(retry_after_hdr)
                                delay = max(
                                    0.0,
                                    (dt - datetime.now(timezone.utc)).total_seconds(),
                                )
                            except Exception:
                                delay = None

                    sleep_for: float = (
                        float(delay)
                        if delay is not None
                        else min(retry_backoff_base * (2**attempt), retry_backoff_max)
                    )
                    try:
                        await resp.read()
                    finally:
                        resp.release()
                    attempt += 1
                    await asyncio.sleep(sleep_for)
                    continue

                resp.raise_for_status()
                async with resp:
                    data = await resp.json()
                return data
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if attempt < retries:
                    sleep_for: float = min(
                        retry_backoff_base * (2**attempt), retry_backoff_max
                    )
                    attempt += 1
                    await asyncio.sleep(sleep_for)
                    continue
                if raise_on_error:
                    raise exc
                return exc
    finally:
        if own_session:
            await session.close()
