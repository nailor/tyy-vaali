from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _

PAPERVOTE = 1
ELECTRONIC = 2
PRE_ELECTRONIC = 3

class Election(models.Model):
    """Election model, automatically generated from WebVoter database"""
    name = models.TextField(primary_key=True)
    password = models.TextField()
    authurl = models.TextField()
    isopen = models.BooleanField()
    production = models.BooleanField()
    ispublic = models.BooleanField()
    firstpassword = models.BooleanField()
    secondpassword = models.BooleanField()
    stv = models.BooleanField()
    government = models.BooleanField()
    toelect = models.IntegerField()
    class Meta:
        db_table = u'election'

class Person(models.Model):
    """Person model.

    This is automatically generated from WebVoter database. WebVoter
    uses Person's hasvoted field to check if a person has voted already.

    WebVoter handles adding persons, the only thing the checker should
    do is to ensure that the person has not voted with either of the
    accounts (if applicable, see below) and mark the hasvoted field
    for the account(s).

    Special notes for election of 2009
    ----------------------------------

    Election has students from two universities, University of Turku
    and Turku School of Economics. That's why the hetu (social
    security number) field is required in the model. This field can be
    removed later. It is used for finding students that are in both
    universities.

    """
    electionname = models.ForeignKey(Election, db_column='electionname')
    personnumber = models.TextField()
    organization = models.TextField()
    lastname = models.TextField(null=True)
    firstname = models.TextField(null=True)
    emailaddress = models.TextField(null=True)
    address = models.TextField(null=True)
    city = models.TextField(null=True)
    zipcode = models.TextField(null=True)
    votedate = models.DateTimeField(null=True)
    hasvoted = models.BooleanField()
    votestyle = models.IntegerField()
    password = models.TextField(null=True)
    hetu = models.TextField()

    def __unicode__(self):
        firstnames = self.firstname.split()
        fn = ' '.join([x.capitalize() for x in firstnames])
        return u'%s, %s' % (self.lastname.capitalize(), fn)


    def check_vote(self):
        """Check if the person has voted.

        Returns True of any instance of the person has voted. False
        otherwise.

        """
        objs = Person.objects.filter(
            hetu__exact=self.hetu,
            hasvoted__exact=True)
        if self.hasvoted or objs.count():
            return True
        return False

    def vote(self):
        """Mark person (and all duplicates) voted.

        Note: this does not check if the person has already voted. Use
        Person.check_vote for that.

        """
        objs = Person.objects.filter(hetu=self.hetu)
        try:
            for p in objs:
                # Votes set this way are paper votes
                p.votestyle = PAPERVOTE
                p.hasvoted = True
                p.save()
        finally:
            # Just a security measure: Mark this user as voted in the
            # end (even if something fails), the check_vote should then
            # return False later on.
            self.votestyle = PAPERVOTE
            self.hasvoted = True
            self.save()

    def get_ticket(self):
        objs = Person.objects.filter(hetu=self.hetu)
        for p in objs:
            if p.ticket_set.all().count() > 0:
                return p.ticket_set.all()
        return None

    def give_slip(self, place):
        """Give person a voting slip and mark person as voted.

        This prevents the electronical voting from working. Votestyle
        is not changed, that is used to determine (in addition to the
        Ticket entry) that the person has a slip, but has not yet
        returned it.

        """
        objs = Person.objects.filter(hetu=self.hetu)
        try:
            for p in objs:
                # Votes set this way are paper votes
                p.hasvoted = True
                p.save()
        finally:
            # Just a security measure: Mark this user as voted in the
            # end (even if something fails), the check_vote should then
            # return False later on.
            self.hasvoted = True
            self.save()
            t = Ticket(
                voter=self,
                release_place=place)
            t.save()

    class Meta:
        db_table = u'person'
	ordering = ['lastname', 'firstname']
        unique_together = ('personnumber', 'organization')

class Place(models.Model):
    name = models.CharField(_(u'name'), max_length=500)
    description = models.TextField(_(u'description'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'voting place')
        verbose_name_plural = _(u'voting places')
        ordering = ['name',]

class Ticket(models.Model):
    voter = models.ForeignKey(Person, verbose_name=_(u'voter'), unique=True)
    release_place = models.ForeignKey(Place,
                                      verbose_name=_(u'release place'),
                                      related_name='released_tickets')
    release_time = models.DateTimeField(_(u'release time'),
                                        default=datetime.now)
    submit_time = models.DateTimeField(_(u'submit time'), null=True)
    submit_place = models.ForeignKey(Place,
                                     verbose_name=_(u'submit place'),
                                     related_name='submitted_tickets',
                                     null=True)

    def __unicode__(self):
        return u'%s, %s (%s)' % (str(self.voter).decode('utf-8'),
                                   self.release_place,
                                   self.release_time)

    class Meta:
        verbose_name = _(u'ticket')
        verbose_name_plural = _(u'tickets')
        ordering = ['release_time',]


