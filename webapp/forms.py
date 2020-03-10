from django import forms
from django.forms import ModelForm
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from webapp.models import Person, LegalName, Location, Partnership, AlternateName

class AddNameForm(ModelForm):
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
    blank_choice = [('','----------------')]
    birth_city = forms.CharField(label='City/Town/Village', 
        max_length=50, required=False)
    birth_state = forms.CharField(label='State/Province/Region',
        max_length=50, required=False)
    birth_country = forms.ChoiceField(label='Country', 
        choices=blank_choice + Location.Country.choices, required=False)

    death_city = forms.CharField(label='City/Town/Village',
        max_length=50, required=False)
    death_state = forms.CharField(label='State/Province/Region', 
        max_length=50, required=False)
    death_country = forms.ChoiceField(label='Country', 
        choices=blank_choice + Location.Country.choices, required=False)

    class Meta:
        model = Person
        fields = ['preferred_name', 'gender', 'birth_date', 'death_date', 
            'living', 'notes']
        widgets = {
            'preferred_name': forms.TextInput(attrs={'size': '40'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 10, 'cols': '50'})
        }

    field_order = ['preferred_name', 'gender', 'birth_date', 'birth_city', 
        'birth_state','birth_country', 'living', 'death_date', 'death_city', 
        'death_state', 'death_country', 'notes']

class AlternateNameForm(ModelForm):
    first_name = forms.CharField(required=False)
    class Meta:
        model = AlternateName
        exclude = ['person','tree']
        widgets = {
            'prefix': forms.TextInput(attrs={'size': '4'}),
            'first_name': forms.TextInput(attrs={'size': '30'}),
            'middle_name': forms.TextInput(attrs={'size': '30'}),
            'last_name': forms.TextInput(attrs={'size': '30'}),
            'suffix': forms.TextInput(attrs={'size': '3'})
        }

AlternateNameFormSet = inlineformset_factory(Person, AlternateName, form=AlternateNameForm, extra=2, can_delete=True)

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
