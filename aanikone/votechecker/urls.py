from django.conf.urls.defaults import *

urlpatterns = patterns(
    'votechecker.views',
    (r'^whois/$', 'whois'),
)
