import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Sized,
    TypeVar,
    overload,
)

from relais.errors import ErrorPolicy, PipelineError
from relais.index import Index
from relais.tasks import CancellationScope

T = TypeVar("T")


@dataclass
class StreamEvent:
    """Event for a stream.

    This class is used to create a stream event for a pipeline.
    """

    pass


@dataclass
class StreamEndEvent(StreamEvent):
    """End event for a stream.

    This class is used to create a stream end event for a pipeline.
    """

    pass


@dataclass
class StreamErrorEvent(StreamEvent):
    """Error event for a stream.

    This class is used to create a stream error event for a pipeline.
    """

    error: PipelineError
    index: Index


@dataclass
class StreamItemEvent(StreamEvent, Generic[T]):
    """Item event for a stream.

    This class is used to create a stream item event for a pipeline.
    """

    item: T
    index: Index


class StreamException(Exception):
    """Exception for a stream.

    This class is used to create a stream exception for a pipeline.
    """

    pass


class StreamAlreadyHasReader(StreamException):
    """Exception for a stream that already has a reader."""

    pass


class StreamAlreadyHasWriter(StreamException):
    """Exception for a stream that already has a writer."""

    pass


class Stream(Generic[T]):
    """Stream for a pipeline.

    This class is used to create a stream for a pipeline.
    """

    def __init__(
        self,
        parent: Optional["Stream[T]"] = None,
        max_size: int = 1000,
        error_policy: ErrorPolicy = ErrorPolicy.FAIL_FAST,
    ):
        self._parent = parent
        self._error_policy = error_policy
        self._max_size = max_size

        # Global cancellation token
        self._cancelled = asyncio.Event() if parent is None else parent._cancelled

        # Completed event
        self._completed = asyncio.Event()

        # Consumed tag
        self._consumed = False

        # Events queue
        self._events: asyncio.Queue[StreamEvent] = asyncio.Queue(maxsize=max_size)

        # Locks
        self._acquire_lock = asyncio.Lock()
        self._has_reader = False
        self._has_writer = False

        self._error: PipelineError | None = None

        # Optional callbacks; can be set by consumers to observe events
        self._on_result_callback: Callable[[Any], Awaitable[Any] | Any] | None = None
        self._on_error_callback: (
            Callable[[PipelineError], Awaitable[Any] | Any] | None
        ) = None

    @property
    def error(self) -> PipelineError | None:
        """Get the error."""
        return self._error

    @classmethod
    async def from_iterable(
        cls, items: Iterable[T], error_policy: ErrorPolicy = ErrorPolicy.FAIL_FAST
    ) -> "Stream[T]":
        """Create a stream from an iterable."""
        # Try to get length for sizing, but default to 0 if not available
        if isinstance(items, Sized):
            max_size = max(1000, len(items) + 1)
        else:
            max_size = 0

        stream = cls(max_size=max_size, error_policy=error_policy)
        stream_writer = await stream.writer()
        for i, item in enumerate(items):
            await stream_writer.write(StreamItemEvent(item=item, index=Index(i)))
        await stream_writer.complete()

        return stream

    async def reader(self) -> "StreamReader[T]":
        """Get a reader for the stream."""
        if self._has_reader:
            raise StreamAlreadyHasReader()

        async with self._acquire_lock:
            if self._has_reader:
                raise StreamAlreadyHasReader()

            self._has_reader = True
            return StreamReader(self)

    async def writer(self) -> "StreamWriter[T]":
        """Get a writer for the stream."""
        if self._has_writer:
            raise StreamAlreadyHasWriter()

        async with self._acquire_lock:
            if self._has_writer:
                raise StreamAlreadyHasWriter()

            self._has_writer = True

        return StreamWriter(self)

    async def cancel(self):
        """Cancel the stream and all its parent and children streams."""
        self._cancelled.set()

    async def complete(self, clear_queue: bool = False):
        """Complete the stream and all its parent streams (since this stream pipes to them)."""
        if self._completed.is_set():
            return

        self._completed.set()

        if self._parent is not None:
            await self._parent.complete(
                clear_queue=True
            )  # Clear the queue of the parent stream

        if clear_queue:
            while not self._events.empty():
                await self._events.get()
        await self._events.put(StreamEndEvent())

    def pipe(self):
        """Pipe the stream to another stream."""
        return Stream(
            parent=self, max_size=self._max_size, error_policy=self._error_policy
        )

    async def handle_error(self, error: StreamErrorEvent):
        """Handle an error."""
        # Invoke error callback regardless of policy
        if self._on_error_callback is not None:
            try:
                maybe = self._on_error_callback(error.error)
                if asyncio.iscoroutine(maybe):
                    await maybe
            except Exception:
                # Callbacks must not break pipeline flow
                pass
        if self._error_policy == ErrorPolicy.FAIL_FAST:
            self._error = error.error
            await self.cancel()
            raise error.error
        elif self._error_policy == ErrorPolicy.COLLECT:
            await self._events.put(error)

    def is_cancelled(self) -> bool:
        """Check if the stream is cancelled."""
        return self._cancelled.is_set()

    def is_completed(self) -> bool:
        """Check if the stream is completed."""
        return self._completed.is_set()

    def cancellation_scope(self) -> CancellationScope:
        """Get the cancellation scope."""
        return CancellationScope([self._cancelled, self._completed])

    async def to_list(self) -> List[StreamItemEvent[T] | StreamErrorEvent]:
        """Get the full list of events ordered by index."""
        items = []
        while not (self.is_cancelled() or self._consumed):
            try:
                next_event = await self._events.get()
                if isinstance(next_event, StreamItemEvent):
                    items.append(next_event)
                elif isinstance(next_event, StreamErrorEvent):
                    items.append(next_event)
                elif isinstance(next_event, StreamEndEvent):
                    self._consumed = True
                    break
            except asyncio.QueueEmpty:
                break

        return sorted(items, key=lambda x: x.index)

    @property
    def consumed(self) -> bool:
        """Check if the stream is consumed."""
        return self._consumed

    def __aiter__(self):
        """Iterate over the stream."""
        return self

    async def __anext__(self) -> StreamItemEvent[T] | StreamErrorEvent:
        """Get the next event."""
        if self.is_cancelled() or self._consumed:
            raise StopAsyncIteration()

        next_event = await self._events.get()
        if isinstance(next_event, StreamItemEvent):
            return next_event
        elif isinstance(next_event, StreamErrorEvent):
            return next_event
        elif isinstance(next_event, StreamEndEvent):
            self._consumed = True
            raise StopAsyncIteration()
        else:
            raise ValueError(f"Invalid event type: {type(next_event)}")

    async def write(self, item: StreamItemEvent[T]):
        """Write an item to the stream."""
        await self._events.put(item)
        # Fire result callback if set
        if self._on_result_callback is not None:
            try:
                maybe = self._on_result_callback(item.item)
                if asyncio.iscoroutine(maybe):
                    await maybe
            except Exception:
                # Suppress callback errors
                pass


class StreamWriter(Generic[T]):
    """Writer for a stream.

    This class is used to write items to a stream.
    """

    def __init__(self, stream: Stream[T]):
        self.stream = stream

    @property
    def error(self) -> PipelineError | None:
        """Get the error."""
        return self.stream.error

    async def handle_error(self, error: StreamErrorEvent):
        """Handle an error."""
        await self.stream.handle_error(error)

    async def write(self, item: StreamItemEvent[T]):
        """Write an item to the stream."""
        await self.stream.write(item)

    def is_cancelled(self) -> bool:
        """Check if the stream is cancelled."""
        return self.stream.is_cancelled()

    def is_completed(self) -> bool:
        """Check if the stream is completed."""
        return self.stream.is_completed()

    def cancellation_scope(self) -> CancellationScope:
        """Get the cancellation scope."""
        return self.stream.cancellation_scope()

    async def complete(self):
        """Complete the stream."""
        await self.stream.complete()

    def is_consumed(self) -> bool:
        """Check if the stream is consumed."""
        return self.stream.consumed


class StreamReader(Generic[T]):
    """Reader for a stream.

    This class is used to read items from a stream.
    """

    _stream: Stream[T]

    def __init__(self, stream: Stream[T]):
        self._stream = stream

    def pipe(self):
        """Pipe the stream to another stream."""
        return self._stream.pipe()

    def is_cancelled(self) -> bool:
        """Check if the stream is cancelled."""
        return self._stream.is_cancelled()

    async def to_list(self) -> List[StreamItemEvent[T] | StreamErrorEvent]:
        """Get the full list of events ordered by index."""
        return await self._stream.to_list()

    @overload
    async def collect(
        self,
        error_policy: Literal[ErrorPolicy.COLLECT],
        *,
        on_result: Callable[[T], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[T | PipelineError]: ...

    @overload
    async def collect(
        self,
        error_policy: Literal[ErrorPolicy.IGNORE, ErrorPolicy.FAIL_FAST],
        *,
        on_result: Callable[[T], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[T]: ...

    @overload
    async def collect(
        self,
        error_policy: None = ...,
        *,
        on_result: Callable[[T], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[T]: ...

    async def collect(
        self,
        error_policy: ErrorPolicy | None = None,
        *,
        on_result: Callable[[T], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ):
        """Collect the stream into a list, handling errors per policy.

        Args:
            error_policy: Optional override for how to handle errors when collecting.
                - FAIL_FAST: raise on first error
                - IGNORE (default behavior if None): skip errors
                - COLLECT: include PipelineError instances in the returned list in index order

        Returns:
            A list of items; with COLLECT, PipelineError objects are interleaved.
        """
        items = await self._stream.to_list()
        results = []

        # Default behavior preserves prior semantics: ignore errors if no policy specified
        effective_policy = (
            error_policy if error_policy is not None else ErrorPolicy.IGNORE
        )

        for item in items:
            if isinstance(item, StreamItemEvent):
                results.append(item.item)  # type: ignore[attr-defined]
            elif isinstance(item, StreamErrorEvent):
                if effective_policy == ErrorPolicy.FAIL_FAST:
                    raise item.error
                elif effective_policy == ErrorPolicy.COLLECT:
                    results.append(item.error)
                # ignore

        return results

    async def cancel(self):
        """Cancel the stream."""
        await self._stream.cancel()

    @property
    def consumed(self) -> bool:
        """Check if the stream is consumed."""
        return self._stream._consumed

    def __aiter__(self) -> AsyncIterator[StreamItemEvent[T] | StreamErrorEvent]:
        """Enter the stream."""
        return self._stream.__aiter__()

    def set_callbacks(
        self,
        *,
        on_result: Callable[[T], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ) -> None:
        """Register callbacks invoked when items or errors occur on the stream.

        These callbacks are best-effort and must not throw; exceptions are suppressed.
        """
        if on_result is not None:
            self._stream._on_result_callback = on_result
        if on_error is not None:
            self._stream._on_error_callback = on_error
