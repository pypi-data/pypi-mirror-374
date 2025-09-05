# rebrandly_otel.py
"""
Rebrandly OpenTelemetry SDK - Simplified instrumentation for Rebrandly services.
"""
import time
import psutil
import functools
from contextlib import contextmanager
from datetime import datetime
from opentelemetry.trace import Status, StatusCode, SpanKind
from typing import Optional, Dict, Any, Callable, TypeVar
from opentelemetry import baggage, propagate, context

from .traces import RebrandlyTracer
from .metrics import RebrandlyMeter
from .logs import RebrandlyLogger


T = TypeVar('T')

class RebrandlyOTEL:
    """Main entry point for Rebrandly's OpenTelemetry instrumentation."""

    _instance: Optional['RebrandlyOTEL'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._tracer: Optional[RebrandlyTracer] = None
            self._meter: Optional[RebrandlyMeter] = None
            self._logger: Optional[RebrandlyLogger] = None
            self.__class__._initialized = True

    def initialize(self, **kwargs) -> 'RebrandlyOTEL':
        # Force initialization of components
        _ = self.tracer
        _ = self.meter
        _ = self.logger

        return self

    @property
    def tracer(self) -> RebrandlyTracer:
        """Get the tracer instance."""
        if self._tracer is None:
            self._tracer = RebrandlyTracer()
        return self._tracer

    @property
    def meter(self) -> RebrandlyMeter:
        """Get the meter instance."""
        if self._meter is None:
            self._meter = RebrandlyMeter()
        return self._meter

    @property
    def logger(self) -> RebrandlyLogger:
        """Get the logger instance."""
        if self._logger is None:
            self._logger = RebrandlyLogger()
        return self._logger

    # Convenience methods for common operations

    @contextmanager
    def span(self,
             name: str,
             attributes: Optional[Dict[str, Any]] = None,
             kind: SpanKind = SpanKind.INTERNAL,
             message=None):
        """Create a span using context manager."""
        with self.tracer.start_span(name, attributes=attributes, kind=kind) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def trace_decorator(self,
                        name: Optional[str] = None,
                        attributes: Optional[Dict[str, Any]] = None,
                        kind: SpanKind = SpanKind.INTERNAL) -> Callable[[T], T]:
        """Decorator for tracing functions."""
        def decorator(func: T) -> T:
            span_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.span(span_name, attributes=attributes, kind=kind):
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    # Fix for the lambda_handler method in rebrandly_otel.py
    # Replace the lambda_handler method (around line 132) with this fixed version:
    def lambda_handler(self,
                       name: Optional[str] = None,
                       attributes: Optional[Dict[str, Any]] = None,
                       kind: SpanKind = SpanKind.SERVER,
                       auto_flush: bool = True,
                       skip_aws_link: bool = False):
        """
        Decorator specifically for Lambda handlers with automatic flushing.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(event=None, lambda_context=None):
                # Determine span name
                span_name = name or f"lambda.{func.__name__}"
                start_time = datetime.now()

                # Build span attributes
                span_attributes = attributes or {}
                span_attributes['faas.trigger'] = self._detect_lambda_trigger(event)

                # Add Lambda-specific attributes if context is available
                if lambda_context is not None:
                    span_attributes.update({
                        "faas.execution": getattr(lambda_context, 'aws_request_id', 'unknown'),
                        "faas.id": getattr(lambda_context, 'function_arn', 'unknown'),
                        "faas.name": getattr(lambda_context, 'function_name', 'unknown'),
                        "faas.version": getattr(lambda_context, 'function_version', 'unknown')
                    })

                # Handle context extraction from AWS events
                token = None
                if not skip_aws_link and event and isinstance(event, dict) and 'Records' in event:
                    first_record = event['Records'][0] if event['Records'] else None
                    if first_record:
                        carrier = {}

                        # Extract from SQS
                        if 'MessageAttributes' in first_record:
                            for key, value in first_record['MessageAttributes'].items():
                                if isinstance(value, dict) and 'StringValue' in value:
                                    carrier[key] = value['StringValue']
                        if ('messageAttributes' in first_record and 'traceparent' in first_record['messageAttributes']
                                and 'stringValue' in first_record['messageAttributes']['traceparent']):
                            carrier['traceparent'] = first_record['messageAttributes']['traceparent']['stringValue']

                        # Extract from SNS
                        elif 'Sns' in first_record and 'MessageAttributes' in first_record['Sns']:
                            for key, value in first_record['Sns']['MessageAttributes'].items():
                                if isinstance(value, dict):
                                    if 'Value' in value:
                                        carrier[key] = value['Value']
                                    elif 'StringValue' in value:
                                        carrier[key] = value['StringValue']

                        # Attach extracted context
                        if carrier:
                            from opentelemetry import propagate, context as otel_context
                            extracted_context = propagate.extract(carrier)
                            token = otel_context.attach(extracted_context)
                            span_attributes['message.has_trace_context'] = True

                result = None
                try:
                    # Increment invocation counter
                    self.meter.GlobalMetrics.invocations.add(1, {'function': span_name})

                    # Create and execute within span
                    with self.tracer.start_span(
                            name=span_name,
                            attributes=span_attributes,
                            kind=kind
                    ) as span:
                        # Add invocation start event
                        span.add_event("lambda.invocation.start", {
                            'event.type': type(event).__name__ if event else 'None'
                        })

                        # Execute handler
                        result = func(event, lambda_context)

                        # Process result
                        self._process_lambda_result(result, span, span_name)

                    return result

                except Exception as e:
                    # Increment error counter
                    self.meter.GlobalMetrics.error_invocations.add(1, {
                        'function': span_name,
                        'error': type(e).__name__
                    })

                    # Log error
                    self.logger.logger.error(f"Lambda execution failed: {e}", exc_info=True)
                    raise

                finally:
                    # Always detach context if we attached it
                    if token is not None:
                        from opentelemetry import context as otel_context
                        otel_context.detach(token)

                    # Record duration
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    self.meter.GlobalMetrics.duration.record(duration, {'function': span_name})

                    # Force flush if enabled
                    if auto_flush:
                        self.logger.logger.info(f"[OTEL] Lambda '{span_name}' completed in {duration:.2f}ms, flushing...")
                        flush_success = self.force_flush(timeout_millis=1000)
                        if not flush_success:
                            self.logger.logger.warning("[OTEL] Force flush may not have completed fully")

            return wrapper
        return decorator

    def _process_lambda_result(self, result, span_context, span_name):
        """Helper method to process Lambda result and update span accordingly"""
        if isinstance(result, dict):
            if 'statusCode' in result:
                span_context.set_attribute("http.status_code", result['statusCode'])
                # Set span status based on HTTP status code
                if result['statusCode'] >= 400:
                    span_context.set_status(Status(StatusCode.ERROR, f"HTTP {result['statusCode']}"))
                else:
                    span_context.set_status(Status(StatusCode.OK))

            # Add completion event
            span_context.add_event("lambda.invocation.complete",
                                   attributes={"success": result.get('statusCode', 200) < 400})
        else:
            span_context.set_status(Status(StatusCode.OK))
            span_context.add_event("lambda.invocation.complete", attributes={"success": True})

        # Increment success counter
        self.meter.GlobalMetrics.successful_invocations.add(1, {'function': span_name})

    def aws_message_handler(self,
                       name: Optional[str] = None,
                       attributes: Optional[Dict[str, Any]] = None,
                       kind: SpanKind = SpanKind.CONSUMER,
                       auto_flush: bool = True):
        """
        require a record object parameter to the function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(record=None, *args, **kwargs):
                # Determine span name
                span_name = name or f"lambda.{func.__name__}"
                start_func = datetime.now()

                # Build span attributes
                span_attributes = attributes or {}

                result = None
                try:
                    # Increment invocations counter
                    print('XXX 2')
                    self.meter.GlobalMetrics.invocations.add(1, {'handler': span_name})

                    # Create span and execute function
                    span_function = self.span
                    if record is not None and 'MessageAttributes' in record:
                        span_function = self.aws_message_span

                    with span_function(span_name, message=record, attributes=span_attributes, kind=kind) as span_context:
                        # Execute the actual handler function
                        result = func(record, *args, **kwargs)

                        # Add result attributes if applicable
                        if result and isinstance(result, dict):
                            if 'statusCode' in result:
                                span_context.set_attribute("handler.status_code", result['statusCode'])

                                # Set span status based on status code
                                if result['statusCode'] >= 400:
                                    span_context.set_status(
                                        Status(StatusCode.ERROR, f"Handler returned {result['statusCode']}")
                                    )
                                else:
                                    span_context.set_status(Status(StatusCode.OK))

                            # Add custom result attributes if present
                            if 'processed' in result:
                                span_context.set_attribute("handler.processed", result['processed'])
                            if 'skipped' in result:
                                span_context.set_attribute("handler.skipped", result['skipped'])

                        # Add completion event
                        span_context.add_event("lambda.invocation.complete", attributes={
                            "handler.success": True
                        })

                        # Increment success counter
                        self.meter.GlobalMetrics.successful_invocations.add(1, {'handler': span_name})

                        return result

                except Exception as e:
                    # Increment error counter
                    self.meter.GlobalMetrics.error_invocations.add(1, {'handler': span_name, 'error': type(e).__name__})

                    # Record the exception in the span
                    span_context.record_exception(e)
                    span_context.set_status(Status(StatusCode.ERROR, str(e)))

                    # Re-raise the exception
                    raise

                finally:
                    if auto_flush:
                        self.force_flush(start_datetime=start_func)

            return wrapper
        return decorator

    def force_flush(self, start_datetime: datetime=None, timeout_millis: int = 1000) -> bool:
        """
        Force flush all telemetry data.
        This is CRITICAL for Lambda functions to ensure data is sent before function freezes.

        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds

        Returns:
            True if all flushes succeeded, False otherwise
        """
        success = True

        if start_datetime is not None:
            end_func = datetime.now()
            duration = (end_func - start_datetime).total_seconds() * 1000
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # Record metrics using standardized names
            self.meter.GlobalMetrics.duration.record(duration, {'source': 'force_flush'})
            self.meter.GlobalMetrics.memory_usage_bytes.set(memory.used)
            self.meter.GlobalMetrics.cpu_usage_percentage.set(cpu_percent)
            self.logger.logger.info(f"Function duration: {duration}ms, Memory usage: {memory.percent}%, CPU usage: {cpu_percent}%")

        try:
            # Flush traces
            if self._tracer:
                if not self._tracer.force_flush(timeout_millis):
                    success = False

            # Flush metrics
            if self._meter:
                if not self._meter.force_flush(timeout_millis):
                    success = False

            # Flush logs
            if self._logger:
                if not self._logger.force_flush(timeout_millis):
                    success = False

            # Add a small delay to ensure network operations complete
            time.sleep(0.1)

        except Exception as e:
            success = False

        return success

    def shutdown(self):
        """
        Shutdown all OTEL components gracefully.
        Call this at the end of your Lambda handler if you want to ensure clean shutdown.
        """
        try:
            if self._tracer:
                self._tracer.shutdown()
            if self._meter:
                self._meter.shutdown()
            if self._logger:
                self._logger.shutdown()
            print("[OTEL] Shutdown completed")
        except Exception as e:
            print(f"[OTEL] Error during shutdown: {e}")

    def _detect_lambda_trigger(self, event: Any) -> str:
        """Detect Lambda trigger type from event."""
        if not event or not isinstance(event, dict):
            return 'direct'

        if 'Records' in event:
            first_record = event['Records'][0] if event['Records'] else None
            if first_record:
                event_source = first_record.get('eventSource', '')
                if event_source == 'aws:sqs':
                    return 'sqs'
                elif event_source == 'aws:sns':
                    return 'sns'
                elif event_source == 'aws:s3':
                    return 's3'
                elif event_source == 'aws:kinesis':
                    return 'kinesis'
                elif event_source == 'aws:dynamodb':
                    return 'dynamodb'

        if 'httpMethod' in event:
            return 'api_gateway'
        if 'requestContext' in event and 'http' in event.get('requestContext', {}):
            return 'api_gateway_v2'
        if event.get('source') == 'aws.events':
            return 'eventbridge'
        if event.get('source') == 'aws.scheduler':
            return 'eventbridge_scheduler'
        if 'jobName' in event:
            return 'batch'

        return 'unknown'

    def set_baggage(self, key: str, value: str):
        """Set baggage item."""
        return baggage.set_baggage(key, value)

    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage item."""
        return baggage.get_baggage(key)

    def inject_context(self, carrier: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inject trace context into headers for outbound requests."""
        if carrier is None:
            carrier = {}
        propagate.inject(carrier)
        return carrier

    def extract_context(self, carrier: Dict[str, Any]) -> context.Context:
        """Extract trace context from incoming request headers."""
        return propagate.extract(carrier)

    def attach_context(self, carrier: Dict[str, Any]) -> object:
        """Extract and attach context, returning a token for cleanup."""
        ctx = self.extract_context(carrier)
        return context.attach(ctx)

    def detach_context(self, token):
        """Detach a previously attached context."""
        context.detach(token)

    @contextmanager
    def aws_message_span(self,
                         name: str,
                         message: Dict[str, Any]=None,
                         attributes: Optional[Dict[str, Any]] = None,
                         kind: SpanKind = SpanKind.CONSUMER):
        """Create span from AWS message - properly handling trace context."""

        from opentelemetry import trace, context as otel_context

        combined_attributes = attributes or {}

        # Extract message attributes for linking/attributes
        if message and isinstance(message, dict):
            # Add message-specific attributes
            if 'Sns' in message:
                sns_msg = message['Sns']
                if 'MessageId' in sns_msg:
                    combined_attributes['messaging.message_id'] = sns_msg['MessageId']
                if 'TopicArn' in sns_msg:
                    combined_attributes['messaging.destination'] = sns_msg['TopicArn']
                combined_attributes['messaging.system'] = 'aws_sns'

                # Check for trace context in SNS
                if 'MessageAttributes' in sns_msg:
                    for key, value in sns_msg['MessageAttributes'].items():
                        if key == 'traceparent' and 'Value' in value:
                            combined_attributes['message.traceparent'] = value['Value']
                            combined_attributes['message.has_trace_context'] = True

            elif 'messageId' in message:
                # SQS message
                combined_attributes['messaging.message_id'] = message['messageId']
                if 'eventSource' in message:
                    combined_attributes['messaging.system'] = message['eventSource']

                # Check for trace context in SQS
                if 'MessageAttributes' in message or 'messageAttributes' in message:
                    attrs = message.get('MessageAttributes') or message.get('messageAttributes', {})
                    for key, value in attrs.items():
                        if key == 'traceparent':
                            tp_value = value.get('StringValue') or value.get('stringValue', '')
                            combined_attributes['message.traceparent'] = tp_value
                            combined_attributes['message.has_trace_context'] = True

            if 'awsRegion' in message:
                combined_attributes['cloud.region'] = message['awsRegion']

        # Use the tracer's start_span method directly to ensure it works
        # This creates a child span of whatever is currently active
        with self.tracer.start_span(
                name=name,
                attributes=combined_attributes,
                kind=kind
        ) as span:
            yield span


# Create Singleton instance
otel = RebrandlyOTEL()

# Export commonly used functions
span = otel.span
aws_message_span = otel.aws_message_span
traces = otel.trace_decorator
tracer = otel.tracer
meter = otel.meter
logger = otel.logger.logger
lambda_handler = otel.lambda_handler
aws_message_handler = otel.aws_message_handler
initialize = otel.initialize
inject_context = otel.inject_context
extract_context = otel.extract_context
attach_context = otel.attach_context
detach_context = otel.detach_context
force_flush = otel.force_flush
shutdown = otel.shutdown