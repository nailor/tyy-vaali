from django.core import serializers
from django.http import (
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseForbidden,
    )
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from aanikone.utils import (
    serialized_json_response,
    json_response,
    serialize_errors,
    )
from aanikone.votechecker.models import Person, Ticket, Place
from aanikone.votechecker.forms import VoterForm
from aanikone.utils import now

@login_required
def index(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render_to_response(
        'index.html',
        {'places': Place.objects.all(),},
        context_instance=RequestContext(request),
        )

@login_required
def whois(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    f = VoterForm(request.POST)
    if f.is_valid():
        return serialized_json_response([f.person])
    return json_response({'errors': serialize_errors(f.errors)})

@login_required
def vote(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    f = VoterForm(request.POST)
    if not f.is_valid():
        return json_response({'errors': serialize_errors(f.errors)})
    if f.person.check_vote():
        if f.person.votestyle >= 2:
            errors = {'__all__': [
                    _('Person has voted electronically on %(day)s at %(time)s') % {
                        'day': f.person.votedate.strftime('%d.%m.%Y'),
                        'time': f.person.votedate.strftime('%H:%M')
                        }
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
                        _('Person has voted in %(place)s on %(day)s at %(time)s') % {
                            'place': ticket.release_place,
                            'day': f.person.votedate.strftime('%d.%m.%Y'),
                            'time': f.person.votedate.strftime('%H:%M'),
                            }]}
        else:
            # Case: Person has received the slip but has not returned it
            ticket = f.person.get_ticket()
            if ticket is None:
                # Fallback in very obscure situation, where person has
                # no tickets but is marked as voted.
                errors = {'__all__': [_('Person has already voted.')]}
            else:
                ticket = ticket[0]
                if ticket.release_place != f.place:
                    return json_response(
                        {'errors': {
                                '__all__': [
                                    _('Error! Ticket is from %s, not here!') % (
                                        ticket.release_place.name)
                                    ]}})
                f.person.vote()
                ticket.submit_place = f.place
                ticket.submit_time = now()
                ticket.save()
                return json_response({'ok': _('OK. Ticket can be stamped.')})
        return json_response({'errors': errors})
    f.person.give_slip(f.place)
    return json_response({'ok': _('OK. Give ticket.')})

@login_required
def ticket_list(request, place_id):
    place = get_object_or_404(Place, pk=place_id)
    tickets = place.find_open_tickets()
    result = []
    for ticket in tickets:
        result.append({
                'number': ticket.voter.personnumber,
                'organization': ticket.voter.organization
                })
    # Do an ugly sort.
    #
    # FIXME: This SHOULD be done in the database level, but I ran out
    # of time to ponder the Django ORM any more
    result.sort(key=lambda x: x['number'])
    return json_response(result)

@login_required
def logout(request):
    response = HttpResponseRedirect(request.META['HTTP_HAKALOGOUTURL'])
    for key, value in request.COOKIES.iteritems():
        response.delete_cookie(key)
    return response

def login_view(request):
    user = authenticate(request=request)
    if user is None:
        return HttpResponseForbidden('You fail :(')
    login(request, user)
    return HttpResponseRedirect('/tarkistus/')
