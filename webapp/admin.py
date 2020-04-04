from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .models import AlternateName, LegalName, Location, Partnership, Person, Tree

text_input_size = 40


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


@admin.register(LegalName)
@admin.register(AlternateName)
class NameAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'middle_name', 'last_name')
    list_display_links = ('id', 'first_name', 'middle_name', 'last_name')
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
    list_display_links = ('city', 'state', 'country')


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

    def first_name(self, obj):
        return obj.legal_name.first_name

    def middle_name(self, obj):
        return obj.legal_name.middle_name

    def last_name(self, obj):
        return obj.legal_name.last_name

    first_name.short_description = 'first name'
    middle_name.short_description = 'middle name'
    last_name.short_description = 'last name'

    list_display = ('id', 'first_name', 'middle_name', 'last_name', 'birth_date', 'living', 'gender', 'tree')
    list_display_links = ('id', 'first_name', 'middle_name', 'last_name')
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': text_input_size})},
        models.CharField: {'widget': TextInput(attrs={'size': text_input_size})},
    }


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    inlines = [PersonInline]

    list_display = ('id', 'partners_str', 'married', 'current')
    list_display_links = ('id', 'partners_str')
