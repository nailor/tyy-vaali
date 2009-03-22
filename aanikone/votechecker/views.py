from django.core import serializers
from django.utils.translation import ugettext as _
from aanikone.utils import (
    serialized_json_response,
    json_response,
    serialize_errors,
    )
from aanikone.votechecker.models import Person, Ticket
from aanikone.votechecker.forms import VoterForm

def whois(request):
    f = VoterForm(request.POST)
    if f.is_valid():
        return serialized_json_response([f.person])
    return json_response({'errors': serialize_errors(f.errors)})

def vote(request):
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
        if f.person.votestyle == 1:
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
        return json_response({'errors': errors})
    t = Ticket(
        voter=f.person,
        release_place=f.place,
        )
    t.save()
    f.person.give_slip()
    return json_response({'ok': _('OK. Give ticket.')})

