from django.db import models

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
    personnumber = models.TextField(primary_key=True)
    lastname = models.TextField(null=True, blank=True)
    firstname = models.TextField(null=True, blank=True)
    emailaddress = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    zipcode = models.TextField(null=True, blank=True)
    votedate = models.DateTimeField(null=True, blank=True)
    hasvoted = models.BooleanField()
    votestyle = models.IntegerField()
    password = models.TextField(null=True, blank=True)
    hetu = models.TextField()
    organization = models.TextField()

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
                p.hasvoted = True
                p.save()
        finally:
            # Just a security measure: Mark this user as voted in the
            # end (even if something fails), the check_vote should then
            # return False later on.
            self.hasvoted = True
            self.save()

    class Meta:
        db_table = u'person'
	ordering = ['lastname', 'firstname']

