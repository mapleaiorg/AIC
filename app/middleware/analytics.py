from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Analytics and logging middleware"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")

        return response
