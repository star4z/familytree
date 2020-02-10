from django.contrib import admin

from .models import AlternateName, LegalName, Parent, Partnership, Person

class PersonInline(admin.TabularInline):
    model = Person

class LegalNameInline(admin.TabularInline):
    model = LegalName

class AlternateNameInline(admin.TabularInline):
    model = AlternateName

class PartnershipInline(admin.TabularInline):
    model = Partnership

class ParentInline(admin.TabularInline):
    model = Parent

def legal_name(obj):
    return LegalName.objects.filter(person=obj)[0]
legal_name.short_description = 'Name'

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [LegalNameInline, AlternateNameInline, PartnershipInline, ParentInline]
    list_display = (legal_name, 'birth_date', 'living', 'gender')
