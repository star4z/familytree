from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .models import Location, Name, Partnership, Person, Tree

text_input_size = 40


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('title',)


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1


class NameInline(admin.TabularInline):
    model = Name
    verbose_name = 'Alternate Name'
    verbose_name_plural = 'Alternate Names'
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [NameInline]
    fieldsets = (
        ('Name', {
            'fields': ('prefix', 'first_name', 'middle_name', 'last_name', 'suffix', 'preferred_name')
        }),
        (None, {
            'fields': (('birth_date', 'birth_location', 'living'), ('death_date', 'death_location'))
        }),
        (None, {
            'fields': ('gender',)
        }),
        ('Partnerships', {
            'fields': ('partnerships',)
        }),
        (None, {
            'fields': ('occupations', 'notes', 'tree')
        })
    )
    list_display = ('first_name', 'last_name', 'birth_date', 'living', 'gender', 'tree')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


def get_partners(obj):
    return ', '.join(str(person) for person in Person.objects.filter(partnerships=obj))


get_partners.short_description = 'Partners'


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    list_display = (get_partners, 'married', 'current')
