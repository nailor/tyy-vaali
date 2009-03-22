from nose.tools import eq_ as eq
from django.test.client import Client

import simplejson

from aanikone.votechecker.models import Election, Person

def test_get_person_data():
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
        organization='tse'
        )
    p.save()
    c = Client()
    response = c.post(
        '/votechecker/whois/',
        {'number': '123',
         'organization': 'tse',}
        )
    eq(response.status_code, 200)
    try:
        c = simplejson.loads(response.content)
    except ValueError, e:
        print response.content
        raise
    eq(len(c), 1)
    
