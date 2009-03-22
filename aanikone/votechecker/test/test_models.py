from nose.tools import eq_ as eq, with_setup

from aanikone.votechecker.models import Election, Person

def test_check_vote_single_person_has_voted():
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
        )
    p.save()
    eq(p.check_vote(), True)

def test_check_vote_single_person_has_not_voted():
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
        personnumber="234",
        electionname=e,
        lastname="bar",
        firstname="foo",
        emailaddress="foo@bar",
        address="...",
        hasvoted=False,
        votestyle=1,
        hetu='faab',
        )
    p.save()
    eq(p.check_vote(), False)

def test_check_vote_multi_person_has_not_voted():
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
    p1 = Person(
        personnumber="345",
        electionname=e,
        lastname="bar",
        firstname="foo",
        emailaddress="foo@bar",
        address="...",
        hasvoted=False,
        votestyle=1,
        hetu='unique',
        )
    p1.save()
    p = Person(
        personnumber="p",
        electionname=e,
        lastname="bar",
        firstname="foo",
        emailaddress="foo@bar",
        address="...",
        hasvoted=False,
        hetu='unique',
        votestyle=1,
        )
    eq(p.check_vote(), False)

def test_check_vote_multi_person_another_has_voted():
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
    p1 = Person(
        personnumber="p1",
        electionname=e,
        hasvoted=True,
        votestyle=1,
        hetu='unique',
        organization='utu',
        )
    p1.save()
    p = Person(
        personnumber="p2",
        electionname=e,
        hasvoted=False,
        hetu='unique',
        votestyle=1,
        organization='tse',
        )
    p.save()
    eq(Person.objects.all().count(), 2)
    eq(p.check_vote(), True)

def test_vote_single_person():
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
        personnumber="singlevote",
        electionname=e,
        address="...",
        hasvoted=False,
        votestyle=0,
        hetu='unique',
        )
    p.save()
    p.vote()
    eq(p.hasvoted, True)

def test_vote_multi_person():
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
    p1 = Person(
        electionname=e,
        hasvoted=False,
        votestyle=1,
        hetu='voted',
        personnumber='1'
        )
    p1.save()
    p = Person(
        electionname=e,
        lastname="bar2",
        firstname="foo2",
        emailaddress="foo@bar2",
        address="...f",
        hasvoted=False,
        hetu='voted',
        votestyle=1,
        personnumber='2'
        )
    p.save()
    p.vote()
    persons = Person.objects.filter(hetu__exact='voted')
    eq(persons.count(), 2)
    for person in persons:
        eq(person.hasvoted, True)