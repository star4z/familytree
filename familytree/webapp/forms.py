from django.forms import ModelForm
from webapp.models import Person, LegalName

class NameForm(ModelForm):
    class Meta:
        model = LegalName
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix',]
        exclude = ['tree']

class addPersonForm(ModelForm):
    class Meta:
        model = Person
        exclude =['legal_name', 'tree']