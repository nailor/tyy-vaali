from nose.tools import eq_ as eq
from django.test.client import Client
from django.contrib.auth.models import User
from django.http import HttpRequest

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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    u = User(username='admin', password='pass')
    u.save()
    ticket = Ticket(
        voter=p,
        release_place=place,
        releaser=u,
        submit_place=place,
        submitter=u,
        )
    ticket.save()
    c = Client()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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

def test_vote_different_submit():
    place = Place(
        name="Testplace",
        description="foo",
        )
    place.save()
    splace = Place(name='Submit')
    splace.save()
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
    u = User(username='admin', password='pass')
    u.save()
    t = Ticket(
        voter=p,
        release_place=place,
        releaser=u,
        )
    t.save()
    c = Client()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 2}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(c, {'errors': {'__all__': [
                    'Error! Ticket is from Testplace, not here!']}})
    tickets = Ticket.objects.all()
    eq(len(tickets), 1)
    eq(tickets[0].voter.id, p.id)
    eq(tickets[0].submit_place, None)

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
    u = User(username='admin', password='pass')
    u.save()
    t = Ticket(
        voter=p,
        release_place=place,
        releaser=u,
        )
    t.save()
    c = Client()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
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
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.get('/tarkistus/whois/')
    eq(response.status_code, 405)

def test_vote_get():
    c = Client()
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.get('/tarkistus/commit/')
    eq(response.status_code, 405)

def test_index_post():
    c = Client()
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.post('/tarkistus/')
    eq(response.status_code, 405)

def test_index_get():
    c = Client()
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.get('/tarkistus/')
    eq(response.status_code, 200)

def test_index_voteplace():
    c = Client()
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    p = Place(name='Foobarland')
    p.save()
    response = c.get('/tarkistus/')
    eq(response.status_code, 200)
    assert 'Foobarland' in response.content

def test_get_tickets_out():
    u = User(username='admin', password='pass')
    u.save()

    place = Place(name='Foobarland')
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
        personnumber="42434",
        electionname=e,
        hasvoted=False,
        votestyle=0,
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    p.give_slip(place, u)
    p = Person(
        personnumber="1234",
        electionname=e,
        hasvoted=False,
        votestyle=0,
        hetu='foob',
        organization='utu.fi',
        id=2,
        )
    p.save()
    p.give_slip(place, u)
    p = Person(
        personnumber="32234",
        electionname=e,
        hasvoted=False,
        votestyle=0,
        hetu='foob',
        organization='tukkk.fi',
        id=3,
        )
    p.save()
    p.give_slip(place, u)
    c = Client()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.get('/tarkistus/list/%d/' % place.id)
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError:
        print response.content
        raise
    eq(len(c), 3)
    eq(c,
       [{'number': '1234', 'organization': 'utu.fi'},
        {'number': '32234', 'organization': 'tukkk.fi'},
        {'number': '42434', 'organization': 'tukkk.fi'},
        ])

def view_empty_tickets_list():
    place = Place(name='Foobarland')
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
    response = c.get('/tarkistus/list/%d/' % place.id)
    eq(response.status_code, 200)
    eq(response.content, simplejson.dump([]))

def test_vote_success_different_orgs_same_person():
    settings.TEST_TIME = datetime(1923, 1, 3)
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
        votestyle=0,
        hetu='foob',
        organization='tukkk.fi',
        id=1,
        )
    p.save()
    p1 = Person(
        personnumber="2345",
        electionname=e,
        hasvoted=False,
        votestyle=0,
        hetu='foob',
        organization='utu.fi',
        id=2,
        )
    p1.save()
    c = Client()
    User(username='admin', password='pass').save()

    fake_request = HttpRequest()
    fake_request.META['HTTP_MAIL'] = 'admin@utu.fi'
    fake_request.META['HTTP_DISPLAYNAME'] = ''
    fake_request.META['HTTP_SN'] = ''

    c.login(request=fake_request)
    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        cont = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(cont, {'ok': 'OK. Give ticket.'})

    verify_p = Person.objects.get(personnumber='2345')
    assert verify_p.hasvoted

    response = c.post(
        '/tarkistus/commit/',
        {'number': '2345', 'organization': 'utu.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        cont = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(cont, {'ok': 'OK. Ticket can be stamped.'})

    response = c.post(
        '/tarkistus/commit/',
        {'number': '2345', 'organization': 'utu.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        cont = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(cont['errors']['__all__'][0],
       'Person has voted in Testplace on 03.01.1923 at 00:00')

    response = c.post(
        '/tarkistus/commit/',
        {'number': '1234', 'organization': 'tukkk.fi', 'place': 1}
        )
    eq(response.status_code, 200)
    try:
        cont = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(cont['errors']['__all__'][0],
       'Person has voted in Testplace on 03.01.1923 at 00:00')
