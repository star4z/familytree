from django.db import models

prefix_choices = tuple()

#Changes where First name and gender(?) has to be mandatory


class Name(models.Model):
    prefix = models.CharField(max_length=7, choices=prefix_choices, blank=True, default='') 
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class LegalName(Name):
    person = models.OneToOneField('Person', on_delete=models.CASCADE)


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING)


class Person(models.Model):
    preferred_name = models.TextField(blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_location = models.TextField(blank=True, default='') #TODO: change to location class
    death_location = models.TextField(blank=True, default='') #TODO: change to location class
    living = models.BooleanField(default=True)
    gender = models.CharField(max_length=100, default='') #Should gender be optional?
    notes = models.TextField(blank=True, default='')
    occupations = models.TextField(blank=True, default='')
    partnerships = models.ManyToManyField('Partnership', blank=True) 
    parents = models.ManyToManyField('Parent', blank=True)

    def __str__(self):
        return f'{LegalName.objects.filter(person=self)[0]}'


class Partnership(models.Model):
    partner = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name='+', null=True)
    children = models.ManyToManyField(Person, related_name='+')
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank =True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    current = models.BooleanField()

    def __str__(self):
        return str(self.partner)


class Parent(models.Model):
    parent = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    biological = models.NullBooleanField(default=None) #Could change back on using booleanField if we only want yes or no 
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return str(self.parent)