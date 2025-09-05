from enum import Enum
from typing import Any, Callable, Mapping, Self, Sequence, Tuple, TypeVar

from sentry_streams.adapters.arroyo.rust_step import RustOperatorFactory
from sentry_streams.pipeline.message import Message

TOut = TypeVar("TOut")

class Route:
    source: str
    waypoints: Sequence[str]

    def __init__(self, source: str, waypoints: Sequence[str]) -> None: ...

class InitialOffset(Enum):
    earliest = "earliest"
    latest = "latest"
    error = "error"

class OffsetResetConfig:
    auto_offset_reset: InitialOffset
    strict_offset_reset: bool

    def __init__(self, auto_offset_reset: InitialOffset, strict_offset_reset: bool) -> None: ...

class PyKafkaConsumerConfig:
    def __init__(
        self,
        bootstrap_servers: Sequence[str],
        group_id: str,
        auto_offset_reset: InitialOffset,
        strict_offset_reset: bool,
        max_poll_interval_ms: int,
        override_params: Mapping[str, str],
    ) -> None: ...

class PyKafkaProducerConfig:
    def __init__(
        self,
        bootstrap_servers: Sequence[str],
        override_params: Mapping[str, str],
    ) -> None: ...

class PyMetricConfig:
    def __init__(
        self,
        host: str,
        port: int,
        tags: dict[str, str] | None,
    ) -> None: ...
    @property
    def host(self) -> str: ...
    @property
    def port(self) -> int: ...
    @property
    def tags(self) -> dict[str, str] | None: ...

class RuntimeOperator:
    @classmethod
    def Map(cls, route: Route, function: Callable[[Message[Any]], Any]) -> Self: ...
    @classmethod
    def Filter(cls, route: Route, function: Callable[[Message[Any]], bool]) -> Self: ...
    @classmethod
    def StreamSink(
        cls, route: Route, topic_name: str, kafka_config: PyKafkaProducerConfig
    ) -> Self: ...
    @classmethod
    def GCSSink(
        cls, route: Route, bucket: str, object_generator: Callable[[], str], thread_count: int
    ) -> Self: ...
    @classmethod
    def Router(
        cls, route: Route, function: Callable[[Message[Any]], str], downstream_routes: Sequence[str]
    ) -> Self: ...
    @classmethod
    def Broadcast(cls, route: Route, downstream_routes: Sequence[str]) -> Self: ...
    @classmethod
    def PythonAdapter(cls, route: Route, delegate_Factory: RustOperatorFactory) -> Self: ...

class ArroyoConsumer:
    def __init__(
        self,
        source: str,
        kafka_config: PyKafkaConsumerConfig,
        topic: str,
        schema: str | None,
        metric_config: PyMetricConfig | None = None,
    ) -> None: ...
    def add_step(self, step: RuntimeOperator) -> None: ...
    def run(self) -> None: ...
    def shutdown(self) -> None: ...

class PyAnyMessage:
    def __init__(
        self,
        payload: Any,
        headers: Sequence[Tuple[str, bytes]],
        timestamp: float,
        schema: str | None,
    ) -> None: ...
    @property
    def payload(self) -> Any: ...
    @property
    def headers(self) -> Sequence[Tuple[str, bytes]]: ...
    @property
    def timestamp(self) -> float: ...
    @property
    def schema(self) -> str | None: ...

class RawMessage:
    def __init__(
        self,
        payload: bytes,
        headers: Sequence[Tuple[str, bytes]],
        timestamp: float,
        schema: str | None,
    ) -> None: ...
    @property
    def payload(self) -> bytes: ...
    @property
    def headers(self) -> Sequence[Tuple[str, bytes]]: ...
    @property
    def timestamp(self) -> float: ...
    @property
    def schema(self) -> str | None: ...

class PyWatermark:
    def __init__(
        self,
        payload: dict[tuple[str, int], int],
        timestamp: int,
    ) -> None: ...
    @property
    def committable(self) -> dict[tuple[str, int], int]: ...
    @property
    def timestamp(self) -> int: ...
