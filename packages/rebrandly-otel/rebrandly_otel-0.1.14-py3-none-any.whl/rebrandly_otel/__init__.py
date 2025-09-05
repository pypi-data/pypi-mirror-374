# src/__init__.py
from .rebrandly_otel import *

# Explicitly define what's available
__all__ = [
    'lambda_handler',
    'span',
    'aws_message_span',
    'traces',
    'tracer',
    'metrics',
    'logger',
    'force_flush',
    'aws_message_handler',
    'shutdown'
]