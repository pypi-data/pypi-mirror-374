import json

from django.contrib import admin
from django.forms import ModelForm, ValidationError

from .models import MockResponse


class MockResponseForm(ModelForm):
    class Meta:
        model = MockResponse
        fields = "__all__"

    def clean_content(self):
        content_type = self.cleaned_data.get("content_type")
        content = self.cleaned_data.get("content")
        if content_type == MockResponse.CONTENT_TYPE__APPLICATION_JSON and content:
            try:
                json.loads(content)
            except TypeError as e:
                raise ValidationError(e.msg)
            except json.JSONDecodeError as e:
                raise ValidationError(e.msg)
        return content


class MockResponseAdmin(admin.ModelAdmin):
    form = MockResponseForm

    def get_content(self, obj):
        max_length = 64
        content = obj.content
        if not content or len(content) <= max_length:
            return content
        return content[:max_length] + " ... ({} chars)".format(len(content) - max_length)

    get_content.short_description = "Content"

    list_display = ["name", "status", "content_type", "get_content"]


admin.site.register(MockResponse, MockResponseAdmin)
