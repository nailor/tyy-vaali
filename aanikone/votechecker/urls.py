from django.conf.urls.defaults import *

urlpatterns = patterns(
    'aanikone.votechecker.views',
    (r'^$', 'index'),
    (r'^whois/$', 'whois'),
    (r'^commit/$', 'vote'),
    (r'^list/([0-9]*)/$', 'ticket_list'),
    (r'^logout/$', 'logout'),
    (r'^login/$', 'login_view'),
)
