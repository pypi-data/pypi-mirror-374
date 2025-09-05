use crate::broadcaster::Broadcaster;
use crate::kafka_config::PyKafkaProducerConfig;
use crate::python_operator::PythonAdapter;
use crate::routers::build_router;
use crate::routes::{Route, RoutedValue};
use crate::sinks::StreamSink;
use crate::store_sinks::GCSSink;
use crate::transformer::{build_filter, build_map};
use crate::utils::traced_with_gil;
use pyo3::prelude::*;
use sentry_arroyo::backends::kafka::producer::KafkaProducer;
use sentry_arroyo::backends::kafka::types::KafkaPayload;
use sentry_arroyo::processing::strategies::run_task_in_threads::ConcurrencyConfig;
use sentry_arroyo::processing::strategies::ProcessingStrategy;

/// RuntimeOperator represent a translated step in the streaming pipeline the
/// Arroyo Rust runtime know how to run.
///
/// This enum is exported to Python as this is the data structure the adapter
/// code builds to instruct the Rust runtime on how to add logic to the
/// pipeline.
///
/// RuntimeOperators do not necessarily map 1:1 to the steps in the python Pipeline
/// data model. This are the operations the Rust runtime can run. Multiple
/// Python pipeline steps may be managed by the same Rust runtime step.
#[pyclass]
#[derive(Debug)]
pub enum RuntimeOperator {
    /// Represents a Map transformation in the streaming pipeline.
    /// This translates to a RunTask step in arroyo where a function
    /// is provided to transform the message payload into a different
    /// one.
    #[pyo3(name = "Map")]
    Map { route: Route, function: Py<PyAny> },

    /// Represents a Filter step in the streaming pipeline.
    /// This translates to a custom Arroyo strategy (Filter step) where a function
    /// is provided to transform the message payload into a bool.
    #[pyo3(name = "Filter")]
    Filter { route: Route, function: Py<PyAny> },

    /// Represents a Kafka Producer as a Sink in the pipeline.
    /// It is translated to an Arroyo Kafka producer.
    #[pyo3(name = "StreamSink")]
    StreamSink {
        route: Route,
        topic_name: String,
        kafka_config: PyKafkaProducerConfig,
    },

    #[pyo3(name = "GCSSink")]
    GCSSink {
        route: Route,
        bucket: String,
        object_generator: Py<PyAny>,
        thread_count: usize,
    },
    /// Represents a Broadcast step in the pipeline that takes a single
    /// message and submits a copy of that message to each downstream route.
    #[pyo3(name = "Broadcast")]
    Broadcast {
        route: Route,
        downstream_routes: Py<PyAny>,
    },
    /// Represents a router step in the pipeline that can send messages
    /// to one of the downstream routes.
    #[pyo3(name = "Router")]
    Router {
        route: Route,
        routing_function: Py<PyAny>,
        downstream_routes: Py<PyAny>,
    },
    /// Delegates messages processing to a Python operator that provides
    /// the same kind of interface as an Arroyo strategy. This is meant
    /// to simplify the porting of python strategies to Rust.
    #[pyo3(name = "PythonAdapter")]
    PythonAdapter {
        route: Route,
        delegate_factory: Py<PyAny>,
    },
}

pub fn build(
    step: &Py<RuntimeOperator>,
    next: Box<dyn ProcessingStrategy<RoutedValue>>,
    terminator_strategy: Box<dyn ProcessingStrategy<KafkaPayload>>,
    concurrency_config: &ConcurrencyConfig,
) -> Box<dyn ProcessingStrategy<RoutedValue>> {
    match step.get() {
        RuntimeOperator::Map { function, route } => {
            // All functions (Python and Rust) are called the same way now
            // Rust functions automatically release the GIL internally
            let func_ref = traced_with_gil!(|py| function.clone_ref(py));
            build_map(route, func_ref, next)
        }
        RuntimeOperator::Filter { function, route } => {
            // All functions (Python and Rust) are called the same way now
            // Rust functions automatically release the GIL internally
            let func_ref = traced_with_gil!(|py| function.clone_ref(py));
            build_filter(route, func_ref, next)
        }
        RuntimeOperator::StreamSink {
            route,
            topic_name,
            kafka_config,
        } => {
            let producer = KafkaProducer::new(kafka_config.clone().into());
            Box::new(StreamSink::new(
                route.clone(),
                producer,
                concurrency_config,
                topic_name,
                next,
                terminator_strategy,
            ))
        }
        RuntimeOperator::GCSSink {
            route,
            bucket,
            object_generator,
            thread_count: _,
        } => {
            let func_ref = traced_with_gil!(|py| { object_generator.clone_ref(py) });

            Box::new(GCSSink::new(
                route.clone(),
                next,
                concurrency_config,
                bucket,
                func_ref,
            ))
        }
        RuntimeOperator::Router {
            route,
            routing_function,
            // TODO: Router step will use downstream_routes once it's fixed to work with watermarks
            #[allow(unused_variables)]
            downstream_routes,
        } => {
            let func_ref = traced_with_gil!(|py| { routing_function.clone_ref(py) });

            build_router(route, func_ref, next)
        }
        RuntimeOperator::PythonAdapter {
            route,
            delegate_factory,
        } => {
            let factory = traced_with_gil!(|py| { delegate_factory.clone_ref(py) });
            Box::new(PythonAdapter::new(route.clone(), factory, next))
        }
        RuntimeOperator::Broadcast {
            route,
            downstream_routes,
        } => {
            let rust_branches =
                traced_with_gil!(|py| { downstream_routes.extract::<Vec<String>>(py).unwrap() });
            Box::new(Broadcaster::new(next, route.clone(), rust_branches))
        }
    }
}
