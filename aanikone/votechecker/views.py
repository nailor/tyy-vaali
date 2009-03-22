from django.core import serializers

from aanikone.utils import serialized_json_response
from aanikone.votechecker.models import Person
from aanikone.votechecker.forms import CheckForm

def whois(request):
    f = CheckForm(request.POST)
    if f.is_valid():
        return serialized_json_response([f.person])
