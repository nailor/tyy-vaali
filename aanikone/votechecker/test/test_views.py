from nose.tools import eq_ as eq
from django.test.client import Client

import simplejson

from datetime import datetime
from django.conf import settings
from aanikone.votechecker.models import (
    Election,
    Person,
    Ticket,
    Place,
    )

def test_get_person_data():
    t = Place(
        name='Testplace',
        description='Foo',
        )
    t.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="123",
        electionname=e,
        lastname="bar",
        firstname="foo",
        emailaddress="foo@bar",
        address="...",
        hasvoted=False,
        votestyle=1,
        hetu='foob',
        organization='tse',
        id=1,
        )
    p.save()
    c = Client()
    response = c.post(
        '/tarkistus/whois/',
        {'number': '123',
         'organization': 'tse',
         'place': 1,}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(len(c), 1)
    eq(c[0]['fields']['personnumber'], '123')

def test_get_person_data_error():
    t = Place(
        name='Testplace',
        description='Foo',
        )
    t.save()
    c = Client()
    response = c.post(
        '/tarkistus/whois/',
        {'number': '123',
         'organization': 'tse',
         'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c,
       {'errors':
            {'__all__': ['Invalid student number']},
        })

def test_get_person_data_no_data():
    c = Client()
    response = c.post(
        '/tarkistus/whois/',
        {}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c,
       {'errors':
            {'number': ['This field is required.'],
             'organization': ['This field is required.'],
             'place': ['This field is required.']},
        })

def test_vote_empty_post():
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c,
       {'errors':
            {'number': ['This field is required.'],
             'organization': ['This field is required.'],
             'place': ['This field is required.'],}
        })

def test_vote_single_already_voted_electronically():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=True,
        votestyle=2,
        votedate=datetime(2009,1,1,18,0),
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError:
        print repr(response.content)
        raise
    eq(
        c['errors'],
        {'__all__': ['Person has voted electronically on 01.01.2009 at 18:00']}
        )

def test_vote_single_already_voted_on_paper():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=True,
        votestyle=1,
        votedate=datetime(2009,1,1,18,0),
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    ticket = Ticket(
        voter=p,
        release_place=place,
        submit_place=place,
        )
    ticket.save()
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError:
        print repr(response.content)
        raise
    eq(
        c['errors'],
        {'__all__': ['Person has voted in Testplace on 01.01.2009 '+
                     'at 18:00']}
        )
def test_vote_no_ticket():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=True,
        votestyle=1,
        votedate=datetime(2009,1,1,18,0),
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError:
        print repr(response.content)
        raise
    eq(
        c['errors'],
        {'__all__': ['Person has already voted.']}
        )

def test_vote_success_single():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=False,
        votestyle=1,
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c, {'ok': 'OK. Give ticket.'})
    tickets = Ticket.objects.all()
    eq(len(tickets), 1)
    eq(tickets[0].voter.id, p.id)

    verify_p = Person.objects.get(personnumber='1234')
    assert verify_p.hasvoted

def test_vote_return_slip():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=True,
        votestyle=0,
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    t = Ticket(
        voter=p,
        release_place=place,
        )
    t.save()
    c = Client()
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c, {'ok': 'OK. Ticket can be stamped.'})
    tickets = Ticket.objects.all()
    eq(len(tickets), 1)
    eq(tickets[0].voter.id, p.id)
    eq(tickets[0].submit_place.id, place.id)

    verify_p = Person.objects.get(personnumber='1234')
    assert verify_p.hasvoted
    eq(verify_p.votestyle, 1)

def test_vote_whole_procedure():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    e = Election(
        name="testelect",
        password="foo",
        authurl="bar",
        isopen=True,
        production=True,
        ispublic=True,
        firstpassword=True,
        secondpassword=True,
        stv=True,
        government=True,
        toelect=100,
        )
    e.save()
    p = Person(
        id=1,
        personnumber="1234",
        electionname=e,
        hasvoted=False,
        votestyle=0,
        hetu='foob',
        organization='tukkk.fi'
        )
    p.save()
    c = Client()
    settings.TEST_TIME = datetime(1900, 1, 1)
    response = c.post('/tarkistus/commit/',
                      {'number': '1234', 'organization': 'tukkk.fi', 'place': 1})
    eq(response.status_code, 200)
    eq(response.content, simplejson.dumps({'ok': 'OK. Give ticket.'}))
    t = Ticket.objects.get(
        release_place=place,
        release_time=datetime(1900, 1, 1),
        voter=p,
        submit_place=None,
        submit_time=None,
        )
    settings.TEST_TIME = datetime(1900, 1, 2)
    response = c.post('/tarkistus/commit/',
                      {'number': '1234', 'organization': 'tukkk.fi', 'place': 1})
    eq(response.status_code, 200)
    eq(response.content,
       simplejson.dumps({'ok': 'OK. Ticket can be stamped.'}))
    t = Ticket.objects.get(
        release_place=place,
        release_time=datetime(1900, 1, 1),
        voter=p,
        submit_place=place,
        submit_time=datetime(1900, 1, 2),
        )

    response = c.post('/tarkistus/commit/',
                      {'number': '1234', 'organization': 'tukkk.fi', 'place': 1})
    eq(response.status_code, 200)
    eq(response.content,
       simplejson.dumps(
            {'errors': {'__all__':
                            ['Person has voted in Testplace on 02.01.1900'+
                             ' at 00:00']}}))
    Person.objects.get(
        personnumber="1234",
        electionname=e,
        hasvoted=True,
        votestyle=1,
        hetu='foob',
        organization='tukkk.fi',
        votedate=datetime(1900, 1, 2),
        id=1,
        )

def test_whois_get():
    c = Client()
    response = c.get('/tarkistus/whois/')
    eq(response.status_code, 405)

def test_vote_get():
    c = Client()
    response = c.get('/tarkistus/commit/')
    eq(response.status_code, 405)

def test_index_post():
    c = Client()
    response = c.post('/tarkistus/')
    eq(response.status_code, 405)

def test_index_get():
    c = Client()
    response = c.get('/tarkistus/')
    eq(response.status_code, 200)

def test_index_voteplace():
    c = Client()
    p = Place(name='Foobarland')
    p.save()
    response = c.get('/tarkistus/')
    eq(response.status_code, 200)
    assert 'Foobarland' in response.content
