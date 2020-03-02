from django import forms
from webapp.models import Person, LegalName
from .submodels.location_model import Location


class NameForm(forms.ModelForm):
    class Meta:
        model = LegalName
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix', ]
        exclude = ['tree']


class AddPersonForm(forms.ModelForm):
    # birth_location = forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,choices=Location.objects.all())
    # death_location = forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,choices=Location.objects.all())

    class Meta:
        model = Person
        exclude = ['legal_name', 'tree']
