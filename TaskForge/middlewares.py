import logging

logger_error = logging.getLogger('task_forge_project_log_file')
logger = logging.getLogger(__name__)

import logging
logger_error = logging.getLogger('hr_log_file')
logger = logging.getLogger(__name__)

"""
Middleware to add log automatically whenever system get any api request.
"""
class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request path starts with '/task-management/'
        if request.path.startswith('/task-management/'):
            # Log information about the request
            logger.info(f"API Request: {request.method} {request.path}, IP: {request.META['REMOTE_ADDR']}")

            response = self.get_response(request)

            # Log information about the response
            logger.info(f"API Response: {response.status_code}")
        else:
            # Skip logging for non-API calls
            response = self.get_response(request)

        return response
