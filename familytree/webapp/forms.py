from django.forms import ModelForm
from django import forms
from webapp.models import Person, LegalName, Location, Partnership


class NameForm(forms.ModelForm):
    class Meta:
        model = LegalName
        exclude = ['tree']
        widgets = {
            'prefix': forms.TextInput(attrs={'size': '4'}),
            'first_name': forms.TextInput(attrs={'size': '30'}),
            'middle_name': forms.TextInput(attrs={'size': '30'}),
            'last_name': forms.TextInput(attrs={'size': '30'}),
            'suffix': forms.TextInput(attrs={'size': '3'})
        }

class AddPersonForm(ModelForm):
    class Meta:
        model = Person
        exclude = ['legal_name', 'tree']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_name': forms.TextInput(attrs={'size': '40'}),
            'notes': forms.Textarea(attrs={'rows': 10, 'cols': '50'})
        }

# Defines a Location form based on the Location model.
# Includes every attribute.
# Textfield sizes for 'city' and 'state' attributes set to 50 characters.
class AddLocationForm(ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'city': forms.TextInput(attrs={'size': '50'}),
            'state': forms.TextInput(attrs={'size': '50'})
        }


class AddPartnershipForm(ModelForm):
    class Meta:
        model = Partnership
        fields = '__all__'
