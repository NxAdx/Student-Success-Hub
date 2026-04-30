import time
from django.core.cache import cache
from django.http import JsonResponse


class CareerCoachRateLimitMiddleware:
    """
    Rate limiting middleware for career coach API endpoints.
    - Guest users: 30 requests/hour (keyed by IP)
    - Authenticated users: 60 requests/hour (keyed by user ID)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to career coach API endpoints
        if not request.path.startswith('/career-coach/api/'):
            return self.get_response(request)

        # Skip rate limiting for key validation (lightweight)
        if request.path.endswith('/validate-key/'):
            return self.get_response(request)

        if request.user.is_authenticated:
            cache_key = f"cc_rate_{request.user.id}"
            limit = 60
        else:
            ip = self._get_client_ip(request)
            cache_key = f"cc_rate_ip_{ip}"
            limit = 30

        # Get current count
        current = cache.get(cache_key, 0)

        if current >= limit:
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': 3600,
            }, status=429)

        # Increment counter (expires after 1 hour)
        cache.set(cache_key, current + 1, timeout=3600)

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
