from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .models import Location, Name, Partnership, Person


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1


class NameInline(admin.TabularInline):
    model = Name
    verbose_name = 'Alternate Name'
    verbose_name_plural = 'Alternate Names'
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': '40'})},
    }


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [NameInline]
    # fields = []
    list_display = ('first_name', 'last_name', 'birth_date', 'living', 'gender')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': '40'})},
    }


def get_partners(obj):
    return ', '.join(str(person) for person in Person.objects.filter(partnerships=obj))


get_partners.short_description = 'Partners'


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    list_display = (get_partners, 'married', 'current')
