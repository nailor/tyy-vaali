import simplejson

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
