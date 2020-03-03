from django.forms import ModelForm
from django import forms
from webapp.models import Person, LegalName, Location

class NameForm(ModelForm):
    class Meta:
        model = LegalName
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix',]
        exclude = ['tree']

class addPersonForm(ModelForm):
    class Meta:
        model = Person
        exclude =['legal_name', 'tree']

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