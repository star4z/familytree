from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .models import AlternateName, LegalName, Location, Name, Partnership, Person, Tree

text_input_size = 40


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(LegalName)
class LegalNameAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1


class AlternateNameInline(admin.TabularInline):
    model = AlternateName
    verbose_name = 'alternate name'
    verbose_name_plural = 'alternate names'
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


class LegalNameInline(admin.TabularInline):
    model = LegalName
    verbose_name = 'legal name'
    verbose_name_plural = 'legal_names'
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')


def get_first_name(obj):
    return obj.legal_name.first_name


def get_middle_name(obj):
    return obj.legal_name.middle_name


def get_last_name(obj):
    return obj.legal_name.last_name


get_first_name.short_description = 'first name'
get_middle_name.short_description = 'middle name'
get_last_name.short_description = 'last name'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [AlternateNameInline]
    fieldsets = (
        ('Name', {
            'fields': ('legal_name',)
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
            'fields': ('notes', 'tree')
        })
    )
    list_display = (get_first_name, get_middle_name, get_last_name, 'birth_date', 'living', 'gender', 'tree')
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
