import logging
import time

from .http_codes import default_http_codes
from .http_headers import (
    HEADER_KEY__HTTP_MOCK_RESPONSE_DELAY_KEY,
    HEADER_KEY__HTTP_MOCK_RESPONSE_ID_KEY,
)
from .models import MockResponse

logger = logging.getLogger(__name__)


class MockResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)  # pragma: no cover

    @staticmethod
    def _calculate_delay_seconds(request):
        mock_response_delay_str = request.META.get(HEADER_KEY__HTTP_MOCK_RESPONSE_DELAY_KEY, None)
        if mock_response_delay_str is not None:
            try:
                return float(mock_response_delay_str)
            except ValueError:
                logger.warning("Invalid mock response delay: {}".format(mock_response_delay_str))
        return 0.0

    def process_view(self, request, view_func, view_args, view_kwargs):
        delay_seconds = self._calculate_delay_seconds(request)
        if delay_seconds > 0:
            time.sleep(delay_seconds)

        mock_response_id = request.META.get(HEADER_KEY__HTTP_MOCK_RESPONSE_ID_KEY, None)
        if mock_response_id is None:
            return None

        mock_obj = None

        try:
            mock = MockResponse.objects.get(name=mock_response_id)
            return mock.get_http_response()
        except MockResponse.DoesNotExist:
            pass

        if mock_response_id in default_http_codes:
            mock_obj = MockResponse(status=default_http_codes[mock_response_id].code)
            return mock_obj.get_http_response()

        if mock_obj is None and mock_response_id is not None:
            logger.warning(
                "Invalid mock response ID: {}. Resuming normal flow ...".format(mock_response_id)
            )

        return None
