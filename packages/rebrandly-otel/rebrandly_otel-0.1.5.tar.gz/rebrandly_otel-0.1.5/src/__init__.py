# src/__init__.py
from .rebrandly_otel import *
from .logs import *  # if you want to expose logs functions
from .metrics import *  # if you want to expose metrics functions
from .traces import *  # if you want to expose traces functions

# Explicitly define what's available
__all__ = [
    'otel',
    'lambda_handler',
    'logger',
    'force_flush',
    # add any other functions/classes you want to expose
]