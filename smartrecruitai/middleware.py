"""
Custom middleware to handle CSRF for REST API
"""

from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token


class EnsureCsrfCookie(MiddlewareMixin):
    """
    Ensure CSRF cookie is set on all pages
    """
    def process_request(self, request):
        # Ensure CSRF token is available
        get_token(request)
        return None

