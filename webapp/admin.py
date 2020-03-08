from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import AlternateName, LegalName, Location, Partnership, Person, Tree

text_input_size = 40


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)


@admin.register(LegalName)
class LegalNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'middle_name', 'last_name')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }

@admin.register(AlternateName)
class AlternateNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'middle_name', 'last_name')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }

class AlternateNameInline(admin.TabularInline):
    model = AlternateName
    verbose_name = 'alternate name'
    verbose_name_plural = 'alternate names'
    extra = 1
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


class PartnershipInline(admin.TabularInline):
    model = Person.partnerships.through
    extra = 1
    verbose_name = 'partnership'
    verbose_name_plural = 'partnerships'


class PersonInline(admin.TabularInline):
    model = Person.partnerships.through
    extra = 1
    verbose_name = 'person'
    verbose_name_plural = 'persons'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [AlternateNameInline, PartnershipInline]
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
        (None, {
            'fields': ('notes', 'tree')
        })
    )
    list_display = ('id', get_first_name, get_middle_name, get_last_name, 'birth_date', 'living', 'gender', 'tree')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


def get_partners(obj: Partnership):
    return obj.partners_str()


get_partners.short_description = 'Partners'


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_display = ('id', get_partners, 'married', 'current')
