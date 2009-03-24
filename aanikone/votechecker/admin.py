from aanikone.votechecker.models import (
    Place,
    Ticket,
    Person,
    )
from django.contrib import admin

admin.site.register(Person)
admin.site.register(Place)
admin.site.register(Ticket)
