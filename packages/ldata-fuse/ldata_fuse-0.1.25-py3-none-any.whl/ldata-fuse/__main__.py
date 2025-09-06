import sys

from latch_o11y.o11y import setup as setup_o11y
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor

sys.stdout.reconfigure(line_buffering=True)

setup_o11y()
AioHttpClientInstrumentor().instrument()

from .app import main

main()
