from aanikone.votechecker.models import Person, Election

def teardown_test_environment():
    Person.objects.all().delete()
    Election.objects.all().delete()
