import simplejson

from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.core import serializers

def json_response(data):
    response = HttpResponse(
        content_type='application/json')
    simplejson.dump(data, response)
    return response

def serialized_json_response(data):
    response = HttpResponse(content_type='application/json')
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(data, ensure_ascii=False, stream=response)
    return response

def serialize_errors(errors):
    # Form errors are a nasty django.utils.functional.__proxy__
    # object, so we need to have some magic here to convert it to dict
    # (which then can be consumed by simplejson).
    return dict(
        (key, [unicode(v) for v in values]) for key,values in errors.items())

def now():
    if hasattr(settings, 'TEST_TIME'):
        return settings.TEST_TIME
    return datetime.now()
