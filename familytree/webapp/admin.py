from django.contrib import admin

from .models import Location
from .models import Person

admin.site.register(Location)
admin.site.register(Person)