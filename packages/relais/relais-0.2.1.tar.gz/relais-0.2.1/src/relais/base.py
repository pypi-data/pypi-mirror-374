import asyncio
from abc import ABC
from asyncio import TaskGroup
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    Literal,
    TypeVar,
    Union,
    cast,
    overload,
)

from relais.errors import ErrorPolicy, PipelineError
from relais.processors import StreamProcessor
from relais.stream import (
    Stream,
    StreamErrorEvent,
    StreamItemEvent,
    StreamReader,
    StreamWriter,
)

# Type variables
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
R = TypeVar("R")


class PipelineSession(Generic[R]):
    """Context manager for streaming pipeline execution.

    Provides controlled execution of pipeline processors with proper resource
    cleanup. Use with async context manager syntax to iterate over stream events
    as they become available.

    Example:
        async with await pipeline.open(data) as stream:
            async for event in stream:
                if isinstance(event, StreamItemEvent):
                    print(f"Result: {event.item}")
    """

    def __init__(
        self,
        processors: list[StreamProcessor[Any, Any]],
        stream: StreamReader[Any],
        error_policy: ErrorPolicy,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ):
        self._task_group = TaskGroup()
        self._processors = processors
        self._processor_tasks = []
        self._stream = stream
        self._error_policy = error_policy
        self._on_result = on_result
        self._on_error = on_error

    async def results(self) -> list[R]:
        collected = await self._stream.collect(self._error_policy)
        return cast(list[R], collected)

    async def __aenter__(self):
        await self._task_group.__aenter__()

        # Ensure callbacks are set before processor tasks start emitting events
        if self._on_result is not None or self._on_error is not None:
            self._stream.set_callbacks(
                on_result=self._on_result, on_error=self._on_error
            )

        for processor in self._processors:
            self._processor_tasks.append(
                self._task_group.create_task(processor.process_stream())
            )

        return self._stream

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._stream.cancel()

        for task in self._processor_tasks:
            if task is not None:
                task.cancel()
        await self._task_group.__aexit__(exc_type, exc_val, exc_tb)


class WithPipeline(ABC, Generic[T, U]):
    """Abstract base for objects that can be chained in pipelines.

    WithPipeline defines the interface for objects that support the pipe
    operator (|) for chaining operations together. This includes both
    individual steps and complete pipelines.

    The class supports two chaining patterns:
    1. step | step  -> Pipeline (forward chaining)
    2. data | step  -> Pipeline (data binding)
    """

    def __or__(self, other: "WithPipeline[U, V]") -> "Pipeline[T, V]":
        """Chain this object with another using | operator.

        Args:
            other: The object to chain after this one

        Returns:
            A new Pipeline containing both objects
        """
        return self.then(other)

    def then(self, other: "WithPipeline[U, V]") -> "Pipeline[T, V]":
        """Chain this object with another sequentially.

        Args:
            other: The object to chain after this one

        Returns:
            A new Pipeline containing both objects

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def __ror__(
        self, other: Union[List[T], Iterable[T], AsyncIterable[T]]
    ) -> "Pipeline[T, U]":
        """Support data | step syntax (reverse pipe operator).

        Args:
            other: The data to pipe into this object

        Returns:
            A new Pipeline with the data as input
        """
        return self.with_input(other)

    def with_input(
        self, data: Union[List[T], Iterable[T], AsyncIterable[T]]
    ) -> "Pipeline[T, U]":
        """Create a pipeline with this object and the given input data.

        Args:
            data: The input data for the pipeline

        Returns:
            A new Pipeline with the specified input

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError


class Step(WithPipeline[T, U]):
    """Base class for individual pipeline steps.

    Step represents a single processing operation that can be chained with other
    steps to form pipelines. Each step defines how to transform input items of
    type T into output items of type U.

    Steps are the building blocks of pipelines and can be:
    - Chained together: step1 | step2 | step3
    - Applied to data: data | step
    - Configured with error policies

    Subclasses must implement _build_processor to define their processing logic.
    """

    async def pipe(
        self, stream_processor: StreamProcessor[Any, T]
    ) -> StreamProcessor[T, U]:
        """Connect this step to an existing processor's output.

        Args:
            stream_processor: The processor whose output becomes this step's input

        Returns:
            A new processor for this step
        """
        return await self.from_stream(stream_processor.output_stream.stream)

    async def from_stream(self, input_stream: Stream[T]) -> StreamProcessor[T, U]:
        """Create a processor for this step from an input stream.

        Args:
            input_stream: The stream to process

        Returns:
            A processor that will execute this step's logic
        """
        output_stream: Stream[U] = cast(Stream[U], input_stream.pipe())
        return self._build_processor(
            await input_stream.reader(), await output_stream.writer()
        )

    def _build_processor(
        self, input_stream: StreamReader[T], output_stream: StreamWriter[U]
    ) -> StreamProcessor[T, U]:
        """Build the processor that implements this step's logic.

        Args:
            input_stream: Stream to read input from
            output_stream: Stream to write output to

        Returns:
            A processor that implements this step

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def then(self, other: WithPipeline[U, V]) -> "Pipeline[T, V]":
        """Chain this step with another step or pipeline.

        Args:
            other: The step or pipeline to execute after this one

        Returns:
            A new Pipeline containing both steps/all steps
        """
        if isinstance(other, Pipeline):
            # If other is a pipeline, create a new pipeline with this step + all other steps
            return Pipeline([self] + other.steps, error_policy=other.error_policy)
        elif isinstance(other, Step):
            # If other is a single step, create a pipeline with both steps
            return Pipeline([self, other])
        else:
            raise ValueError(f"Invalid type: {type(other).__name__}")

    def with_input(
        self, data: Union[List[T], Iterable[T], AsyncIterable[T]]
    ) -> "Pipeline[T, U]":
        """Create a pipeline with this step and input data.

        Args:
            data: The input data for the pipeline

        Returns:
            A new Pipeline with this step and the specified input
        """
        return Pipeline([self], input_data=data)

    def with_error_policy(self, error_policy: ErrorPolicy) -> "Pipeline[T, U]":
        """Create a pipeline with this step and a specific error policy.

        Args:
            error_policy: How to handle errors during processing

        Returns:
            A new Pipeline with this step and the specified error policy
        """
        return Pipeline([self], error_policy=error_policy)


class Pipeline(Step[T, U]):
    """High-performance streaming pipeline for concurrent data processing.

    Pipeline provides a streaming architecture where data flows through bounded
    async queues between processing steps. All operations run concurrently with
    proper backpressure handling and memory management.

    Key Features:
    - **True Streaming**: Data flows immediately between steps
    - **Directional Cancellation**: Operations like take() cancel upstream processing
    - **Concurrent Execution**: All async operations run in parallel
    - **Memory Bounded**: Configurable queue sizes prevent memory explosions
    - **Flexible Error Handling**: FAIL_FAST, IGNORE, or COLLECT error policies

    Usage Patterns:
        # Basic pipeline with chaining
        result = await (data | r.Map(transform) | r.Filter(validate) | r.Take(10)).collect()

        # Streaming results as they arrive
        async for item in (data | pipeline).stream():
            process(item)

        # Error handling
        pipeline = r.Pipeline([r.Map(might_fail)], error_policy=ErrorPolicy.IGNORE)
        results = await pipeline.collect(data)

        # Context manager for fine-grained control
        async with await pipeline.open(data) as stream:
            async for event in stream:
                handle_event(event)

    Performance Characteristics:
    - Optimal for I/O-bound operations (API calls, file processing)
    - Handles 100-100K items efficiently
    - Memory usage bounded regardless of input size
    - Early termination optimizations (take(), skip())

    Attributes:
        steps: List of processing steps to execute sequentially
        input_data: Optional input data bound to the pipeline
        error_policy: How to handle processing errors (FAIL_FAST, IGNORE, COLLECT)
    """

    steps: List[Step[Any, Any]]

    def __init__(
        self,
        steps: List[Step[Any, Any]],
        input_data: Iterable[T] | AsyncIterable[T] | None = None,
        error_policy: ErrorPolicy = ErrorPolicy.FAIL_FAST,
    ):
        """Initialize a new Pipeline.

        Args:
            steps: List of steps to execute in sequence
            input_data: Optional input data for the pipeline
            error_policy: How to handle errors during processing
        """
        if not isinstance(steps, list):
            raise TypeError(f"steps must be a list, got {type(steps).__name__}")
        if not isinstance(error_policy, ErrorPolicy):
            raise TypeError(
                f"error_policy must be an ErrorPolicy, got {type(error_policy).__name__}"
            )

        self.steps = steps
        self.input_data = input_data
        self.error_policy = error_policy

    async def _get_input_stream(
        self, input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None
    ) -> Stream[T]:
        """Convert input data to a Stream for pipeline processing.

        This method handles different types of input data and converts them
        to the Stream format required by the pipeline. It supports:
        - Existing Stream objects (reused with updated error policy)
        - Async iterators (wrapped with AsyncIteratorStep)
        - Regular iterables (converted to Stream)

        Args:
            input_data: Input data to convert to a stream

        Returns:
            A Stream ready for pipeline processing

        Raises:
            ValueError: If no input is provided or input is provided twice
        """
        data_to_process = input_data if input_data is not None else self.input_data

        if data_to_process is None:
            raise ValueError("No input provided")

        if input_data is not None and self.input_data is not None:
            raise ValueError("Input provided twice")

        # Check if it's actually a Stream object
        if isinstance(data_to_process, Stream):
            # Update the input stream's error policy to match pipeline
            data_to_process._error_policy = self.error_policy
            return data_to_process

        # Check if it's an async iterator
        elif hasattr(data_to_process, "__aiter__"):
            # TODO: make this cleaner
            # Use AsyncIteratorStep to handle async iteration lazily
            from .steps.async_iterator_step import AsyncIteratorStep

            async_step = AsyncIteratorStep(cast(AsyncIterator[T], data_to_process))

            # Create a dummy input stream (empty)
            dummy_input = Stream[None](error_policy=self.error_policy)
            dummy_writer = await dummy_input.writer()
            await (
                dummy_writer.complete()
            )  # End it immediately since async iterator step doesn't need input

            # Create the processor and get its output stream
            processor = await async_step.from_stream(dummy_input)

            # We need to start the processor to begin feeding the stream
            asyncio.create_task(processor.process_stream())

            return processor.output_stream.stream
        else:
            # It's a regular sync iterable
            return await Stream.from_iterable(
                cast(Iterable[T], data_to_process), self.error_policy
            )

    @overload
    async def open(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.COLLECT] = ErrorPolicy.COLLECT,
        *,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> PipelineSession[U | PipelineError]: ...

    @overload
    async def open(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.IGNORE] = ErrorPolicy.IGNORE,
        *,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> PipelineSession[U]: ...

    @overload
    async def open(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.FAIL_FAST] = ErrorPolicy.FAIL_FAST,
        *,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> PipelineSession[U]: ...

    @overload
    async def open(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: None = ...,
        *,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> PipelineSession[U]: ...

    async def open(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: ErrorPolicy | None = None,
        *,
        on_result: Callable[[Any], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ) -> PipelineSession[Any]:
        """Prepare a session for executing the pipeline.

        This method builds a chain of processors where each processor's output
        becomes the next processor's input, and returns a context manager that
        controls their execution and lifecycle.

        Args:
            input_data: Input data to process through the pipeline
            error_policy: Optional override for this run's error handling policy

        Returns:
            PipelineSession containing processors and output stream reader
        """
        effective_pipeline = (
            self.with_error_policy(cast(ErrorPolicy, error_policy))
            if error_policy is not None
            else self
        )

        processors = []
        input_stream = await effective_pipeline._get_input_stream(input_data)
        for step in effective_pipeline.steps:
            output_stream = input_stream.pipe()
            processor = step._build_processor(
                await input_stream.reader(), await output_stream.writer()
            )
            processors.append(processor)
            input_stream = output_stream

        return PipelineSession(
            processors,
            cast(StreamReader[Any], await input_stream.reader()),
            effective_pipeline.error_policy,
            on_result=on_result,
            on_error=on_error,
        )

    @overload
    async def collect(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.FAIL_FAST] = ErrorPolicy.FAIL_FAST,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[U]: ...

    @overload
    async def collect(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.COLLECT] = ErrorPolicy.COLLECT,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[U | PipelineError]: ...

    @overload
    async def collect(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.IGNORE] = ErrorPolicy.IGNORE,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[U]: ...

    @overload
    async def collect(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: None = ...,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> list[U]: ...

    async def collect(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: ErrorPolicy | None = None,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ):
        """Execute pipeline and collect all results into a list.

        This method runs the entire pipeline to completion and returns all
        successful results. For streaming processing of large datasets, consider
        using stream() instead to process items as they become available.

        Args:
            input_data: Optional input data (overrides constructor input_data)
            error_policy: Optional override of this run's error handling policy.

        Returns:
            - If error policy is IGNORE or None: list of successful results
            - If error policy is COLLECT: list containing results and PipelineError objects

        Raises:
            PipelineError: If execution fails and error policy is FAIL_FAST

        Example:
            # Basic collection
            results = await (range(10) | r.Map(lambda x: x * 2)).collect()

            # With runtime input
            pipeline = r.Map(str.upper) | r.Filter(lambda s: len(s) > 3)
            results = await pipeline.collect(['hello', 'world', 'foo'])

            # Collect with errors included (asyncio.gather-style)
            combined = await pipeline.with_error_policy(ErrorPolicy.COLLECT).collect(['a', 'b'], error_policy=ErrorPolicy.COLLECT)
            # Separate results from errors
            data = [x for x in combined if not isinstance(x, PipelineError)]
            errors = [x for x in combined if isinstance(x, PipelineError)]
        """
        effective_pipeline = (
            self.with_error_policy(cast(ErrorPolicy, error_policy))
            if error_policy is not None
            else self
        )
        try:
            async with await effective_pipeline.open(
                input_data,
                on_result=cast(Callable[[Any], Awaitable[Any] | Any] | None, on_result),
                on_error=on_error,
            ) as result:
                return await result.collect(
                    error_policy,
                    on_result=cast(
                        Callable[[Any], Awaitable[Any] | Any] | None, on_result
                    ),
                    on_error=on_error,
                )
        except ExceptionGroup as e:
            for error in e.exceptions:
                if isinstance(error, PipelineError):
                    raise error
            raise e

    @overload
    def stream(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.FAIL_FAST] = ErrorPolicy.FAIL_FAST,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> AsyncIterator[U]: ...

    @overload
    def stream(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.COLLECT] = ErrorPolicy.COLLECT,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> AsyncIterator[U | PipelineError]: ...

    @overload
    def stream(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: Literal[ErrorPolicy.IGNORE] = ErrorPolicy.IGNORE,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> AsyncIterator[U]: ...

    @overload
    def stream(
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: None = ...,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = ...,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = ...,
    ) -> AsyncIterator[U]: ...

    async def stream(  # pyright: ignore[reportInconsistentOverload] Know bug in pyright
        self,
        input_data: Union[Stream[T], Iterable[T], AsyncIterable[T]] | None = None,
        error_policy: ErrorPolicy | None = None,
        *,
        on_result: Callable[[U], Awaitable[Any] | Any] | None = None,
        on_error: Callable[[PipelineError], Awaitable[Any] | Any] | None = None,
    ):
        """Execute pipeline and stream results as they become available.

        This method provides true streaming processing where results are yielded
        immediately as they're produced by the pipeline. Items are processed
        concurrently and yielded in completion order (not input order).

        Perfect for:
        - Processing large datasets with bounded memory
        - Real-time data processing
        - Early result consumption without waiting for pipeline completion

        Args:
            input_data: Optional input data (overrides constructor input_data)
            error_policy: Optional override for this run's error handling policy.

        Yields:
            - If IGNORE or None: only successful results
            - If COLLECT: results and PipelineError objects as they occur

        Raises:
            PipelineError: If execution fails and error policy is FAIL_FAST
            ValueError: If no input data is provided

        # Type hint overloads for stream
        # IGNORE/FAIL_FAST -> AsyncIterator[U]
        # COLLECT -> AsyncIterator[U | PipelineError]

        Example:
            # Process large dataset with bounded memory
            async for batch in (huge_dataset | r.Map(transform) | r.Batch(100)).stream():
                save_batch(batch)  # Process immediately, don't accumulate

            # Early result consumption
            pipeline = data | r.Map(expensive_async_op) | r.Filter(validate)
            async for result in pipeline.stream():
                if is_what_we_need(result):
                    return result  # Early termination saves processing

            # Stream with errors included
            async for item in pipeline.with_error_policy(ErrorPolicy.COLLECT).stream(error_policy=ErrorPolicy.COLLECT):
                if isinstance(item, PipelineError):
                    handle_error(item)
                else:
                    handle_result(item)
        """
        effective_pipeline = (
            self.with_error_policy(cast(ErrorPolicy, error_policy))
            if error_policy is not None
            else self
        )
        async with await effective_pipeline.open(
            input_data,
            on_result=cast(Callable[[Any], Awaitable[Any] | Any] | None, on_result),
            on_error=on_error,
        ) as result:
            async for item in result:
                if isinstance(item, StreamItemEvent):
                    yield item.item
                elif isinstance(item, StreamErrorEvent) and (
                    error_policy == ErrorPolicy.COLLECT
                ):
                    yield item.error

    def then(self, other: WithPipeline[U, V]) -> "Pipeline[T, V]":
        """Chain this pipeline with another step or pipeline."""
        if isinstance(other, Pipeline):
            # If other is a pipeline, merge all steps together
            merged_steps = self.steps + other.steps
            # Use the error policy from the first pipeline unless the second has a different one
            merged_error_policy = (
                other.error_policy
                if other.error_policy != ErrorPolicy.FAIL_FAST
                else self.error_policy
            )
            return Pipeline(
                merged_steps,
                input_data=self.input_data,
                error_policy=merged_error_policy,
            )
        elif isinstance(other, Step):
            # If other is a single step, add it to our steps
            return Pipeline(
                self.steps + [other],
                input_data=self.input_data,
                error_policy=self.error_policy,
            )
        else:
            raise ValueError(f"Invalid type: {type(other).__name__}")

    def with_input(
        self, data: Union[List[T], Iterable[T], AsyncIterable[T]]
    ) -> "Pipeline[T, U]":
        """Support data | step syntax."""
        if self.input_data is not None:
            raise ValueError("Input provided twice")

        return Pipeline(self.steps, input_data=data, error_policy=self.error_policy)

    def with_error_policy(self, error_policy: ErrorPolicy) -> "Pipeline[T, U]":
        """Set error policy for this pipeline."""
        return Pipeline(
            self.steps, input_data=self.input_data, error_policy=error_policy
        )
