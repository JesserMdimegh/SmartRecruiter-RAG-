"""
Custom mixins for ViewSets
"""

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import CsrfViewMiddleware


class CSRFExemptMixin:
    """
    Mixin to exempt ViewSet from CSRF for development
    This works with Django REST Framework ViewSets
    """
    def dispatch(self, request, *args, **kwargs):
        # Disable CSRF check for this view
        setattr(request, '_dont_enforce_csrf_checks', True)
        return super().dispatch(request, *args, **kwargs)

