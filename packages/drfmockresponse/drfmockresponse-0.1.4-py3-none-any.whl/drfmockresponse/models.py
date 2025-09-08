from django.db import models
from django.http import HttpResponse

from .content_types import ContentTypeApplicationJSON, ContentTypePlainText
from .http_codes import default_http_codes


class MockResponse(models.Model):
    class Meta:
        verbose_name_plural = "Mock Responses"

    STATUS_CHOICES = [(int(key), value.name) for key, value in default_http_codes.items()]

    CONTENT_TYPE__PLAIN_TEXT = 0
    CONTENT_TYPE__APPLICATION_JSON = 1
    CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE__PLAIN_TEXT, ContentTypePlainText.type),
        (CONTENT_TYPE__APPLICATION_JSON, ContentTypeApplicationJSON.type),
    )

    name = models.CharField(unique=True, max_length=128, blank=False, null=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, blank=False, null=False)
    content_type = models.PositiveSmallIntegerField(
        choices=CONTENT_TYPE_CHOICES, default=CONTENT_TYPE__PLAIN_TEXT, blank=False, null=False
    )
    content = models.TextField(blank=True, null=True)

    @property
    def content_type__str__(self):
        return MockResponse.CONTENT_TYPE_CHOICES[self.content_type][1]

    def get_http_response(self):
        if self.content is not None:
            return HttpResponse(
                status=self.status, content_type=self.content_type__str__, content=self.content
            )
        return HttpResponse(status=self.status, content_type=self.content_type__str__)

    def __str__(self):
        return self.name
