from nose.tools import eq_ as eq

import simplejson

from django.http import HttpResponse
from django import forms

from aanikone import utils
from aanikone.votechecker.models import Election, Person

def test_json_response():
    a = utils.json_response({'foo': 'bar'})
    assert isinstance(a, HttpResponse)
    eq(a['Content-Type'], 'application/json')
    eq(a.content, simplejson.dumps({'foo': 'bar'}))

def test_json_serializer():
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
        hasvoted=True,
        votestyle=1,
        hetu='foob',
        organization='tse.fi',
        )
    p.save()

    person = Person.objects.get(personnumber='123')
    r = utils.serialized_json_response([person])
    assert isinstance(r, HttpResponse)
    eq(r['Content-Type'], 'application/json')
    try:
        c = simplejson.loads(r.content)
    except ValueError:
        print repr(r.content)
        raise
    c = c[0]
    eq(c['model'], 'votechecker.person')
    eq(c['fields'], {
            'personnumber': '123',
            'hasvoted': True,
            'city': None,
            'firstname': None,
            'electionname': 'testelect',
            'votestyle': 1,
            'hetu': 'foob',
            'votedate': None,
            'emailaddress': None,
            'address': None,
            'zipcode': None,
            'organization': 'tse.fi',
            'password': None,
            'lastname': None,
            })

def test_serialize_errors():
    class TestForm(forms.Form):
        f = forms.CharField()

    testform = TestForm({})
    assert not testform.is_valid()
    eq(utils.serialize_errors(testform.errors),
       {'f': ['This field is required.']}
       )

def test_serialize_errors_form_ok():
    class TestForm(forms.Form):
        f = forms.CharField()

    testform = TestForm({'f': 'foo'})
    assert testform.is_valid()
    eq(utils.serialize_errors(testform.errors), {})
