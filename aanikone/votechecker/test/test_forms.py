from nose.tools import eq_ as eq

from aanikone.votechecker.models import Election, Person, Place
from aanikone.votechecker.forms import VoterForm

def test_form_empty():
    f = VoterForm({})
    assert not f.is_valid()
    eq(f.errors,
       {
            'number': ['This field is required.'],
            'organization': ['This field is required.'],
            'place': ['This field is required.'],
            }
       )

def test_form_wrong_number():
    t = Place(
        name='Testplace',
        description='Foo',
        )
    t.save()
    f = VoterForm({
            'organization': 'utu.fi',
            'number': '12345',
            'place': '1'})
    assert not f.is_valid()
    eq(f.errors,
       {
            '__all__': ['Invalid student number']
            })

def test_form_wrong_org():
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
        hasvoted=True,
        votestyle=1,
        hetu='foob',
        organization='utu.fi',
        )
    p.save()
    f = VoterForm({'organization': 'tse.fi', 'number': '123', 'place': 1})
    assert not f.is_valid()
    eq(f.errors,
       {
            '__all__': ['Invalid student number']
            })

def test_form_correct_data():
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
        hasvoted=True,
        votestyle=1,
        hetu='foob',
        organization='utu.fi',
        )
    p.save()
    f = VoterForm({'organization': 'utu.fi', 'number': '123', 'place': 1})
    assert f.is_valid()
    eq(f.errors, {})
    eq(f.person.personnumber, "123")
