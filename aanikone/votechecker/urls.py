from django.conf.urls.defaults import *

urlpatterns = patterns(
    'aanikone.votechecker.views',
    (r'^$', 'index'),
    (r'^whois/$', 'whois'),
    (r'^vote/$', 'vote'),
)
