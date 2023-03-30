from flask import request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import settings


def configure_tracer() -> None:
    if not settings.DEBUG:  # отключаем если не prod
        trace.set_tracer_provider(TracerProvider(resource=Resource({'service.name': 'Auth API'})))
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=settings.JAEGER_HOST,
                    agent_port=int(settings.JAEGER_PORT),
                )
            )
        )
        # Чтобы видеть трейсы в консоли
        # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


def init_tracer(app):
    if not settings.DEBUG:  # отключаем если не prod
        FlaskInstrumentor().instrument_app(app)

        @app.before_request
        def before_request_id():
            request_id = request.headers.get('X-Request-Id')
            tracer = trace.get_tracer(__name__)
            span = tracer.start_span(__name__)
            span.set_attribute('http.request_id', request_id)
            span.end()
            if not request_id:
                raise RuntimeError('request id is required')
