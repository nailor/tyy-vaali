from nose.tools import eq_ as eq

from aanikone.votechecker.models import Election, Person
from aanikone.votechecker.forms import CheckForm

def test_form_empty():
    f = CheckForm({})
    assert not f.is_valid()
    eq(f.errors,
       {
            'number': ['This field is required.'],
            'organization': ['This field is required.'],
            }
       )

def test_form_wrong_number():
    f = CheckForm({'organization': 'utu.fi', 'number': '12345'})
    assert not f.is_valid()
    eq(f.errors,
       {
            '__all__': ['Invalid student number']
            })

def test_form_wrong_org():
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
    f = CheckForm({'organization': 'tse.fi', 'number': '123'})
    assert not f.is_valid()
    eq(f.errors,
       {
            '__all__': ['Invalid student number']
            })

def test_form_correct_data():
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
    f = CheckForm({'organization': 'utu.fi', 'number': '123'})
    assert f.is_valid()
    eq(f.errors, {})
    eq(f.person.personnumber, "123")
