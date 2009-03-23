from django.core import serializers
from django.http import HttpResponseNotAllowed
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext

from aanikone.utils import (
    serialized_json_response,
    json_response,
    serialize_errors,
    )
from aanikone.votechecker.models import Person, Ticket
from aanikone.votechecker.forms import VoterForm
from aanikone.utils import now

def index(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render_to_response(
        'index.html',
        context_instance=RequestContext(request),
        )

def whois(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    f = VoterForm(request.POST)
    if f.is_valid():
        return serialized_json_response([f.person])
    return json_response({'errors': serialize_errors(f.errors)})

def vote(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    f = VoterForm(request.POST)
    if not f.is_valid():
        return json_response({'errors': serialize_errors(f.errors)})
    if f.person.check_vote():
        if f.person.votestyle >= 2:
            errors = {'__all__': [
                    _('Person has voted electronically on %s') % (
                        f.person.votedate.strftime('%d.%m.%Y at %H:%M')
                        )
                    ]}
        elif f.person.votestyle == 1:
            ticket = f.person.get_ticket()
            if ticket is None:
                # Fallback in very obscure situation, where person has
                # no tickets but is marked as voted.
                errors = {'__all__': [_('Person has already voted.')]}
            else:
                ticket = ticket[0]
                errors = {'__all__': [
                        _('Person has voted in %s on %s') % (
                            ticket.release_place,
                            f.person.votedate.strftime('%d.%m.%Y at %H:%M')
                            )]}
        else:
            # Case: Person has received the slip but has not returned it
            ticket = f.person.get_ticket()
            if ticket is None:
                # Fallback in very obscure situation, where person has
                # no tickets but is marked as voted.
                errors = {'__all__': [_('Person has already voted.')]}
            else:
                ticket = ticket[0]
                f.person.vote()
                ticket.submit_place = f.place
                ticket.submit_time = now()
                ticket.save()
                return json_response({'ok': 'OK. Ticket can be stamped.'})
        return json_response({'errors': errors})
    f.person.give_slip(f.place)
    return json_response({'ok': _('OK. Give ticket.')})

