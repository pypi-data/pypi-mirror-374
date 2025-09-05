from datetime import timedelta
from typing import MutableSequence, Optional, Self, Tuple

from sentry_kafka_schemas.schema_types.ingest_metrics_v1 import IngestMetric

from sentry_streams.pipeline import streaming_source
from sentry_streams.pipeline.function_template import Accumulator
from sentry_streams.pipeline.message import Message
from sentry_streams.pipeline.pipeline import (
    Parser,
    Reducer,
    Serializer,
    StreamSink,
)
from sentry_streams.pipeline.window import SlidingWindow

# The simplest possible pipeline.
# - reads from Kafka
# - parses the metric data, validating against schema
# - batches messages together, emits aggregate results based on sliding window configuration
# - serializes the result into bytes
# - produces the event on Kafka


class TransformerBatch(
    Accumulator[Message[IngestMetric], MutableSequence[Tuple[IngestMetric, Optional[str]]]]
):

    def __init__(self) -> None:
        self.batch: MutableSequence[Tuple[IngestMetric, Optional[str]]] = []

    def add(self, value: Message[IngestMetric]) -> Self:
        self.batch.append((value.payload, value.schema))

        return self

    def get_value(self) -> MutableSequence[Tuple[IngestMetric, Optional[str]]]:
        return self.batch

    def merge(self, other: Self) -> Self:
        self.batch.extend(other.batch)

        return self


reduce_window = SlidingWindow(window_size=timedelta(seconds=6), window_slide=timedelta(seconds=2))

pipeline = streaming_source(
    name="myinput", stream_name="ingest-metrics"
)  # ExtensibleChain[Message[bytes]]

chain1 = pipeline.apply(
    Parser[IngestMetric]("parser"),  # pass in the standard message parser function
)  # ExtensibleChain[Message[IngestMetric]]

chain2 = chain1.apply(
    Reducer("custom_batcher", reduce_window, TransformerBatch)
)  # ExtensibleChain[Message[MutableSequence[IngestMetric]]]

chain3 = chain2.apply(
    Serializer("serializer"),  # pass in the standard message serializer function
)  # ExtensibleChain[bytes]

chain4 = chain3.sink(StreamSink("kafkasink2", stream_name="transformed-events"))  # Chain
