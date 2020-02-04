from django.db import models

prefix_choices = tuple()


class Name(models.Model):
    prefix = models.CharField(max_length=7, choices=prefix_choices, blank=True) 
    first_name = models.TextField()
    middle_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    suffix = models.CharField(max_length=6, blank=True)


class LegalName(Name):
    pass


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING)


class Person(models.Model):
    name = models.OneToOneField(LegalName, on_delete=models.CASCADE)
    preferred_name = models.TextField(blank=True)
    birth_date = models.DateField(null=True)
    death_date = models.DateField(null=True)
    birth_location = models.TextField(blank=True) #TODO: change to location class
    death_location = models.TextField(blank=True) #TODO: change to location class
    living = models.BooleanField(default='TRUE')
    gender = models.CharField(max_length=100) #Should gender be optional?
    notes = models.TextField(blank=True)
    occupations = models.TextField(blank=True)
    partnerships = models.ManyToManyField('Partnership', blank=True, null=True) 
    parents = models.ManyToManyField('Parent', blank=True, null=True)


class Partnership(models.Model):
    partner = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name='+', null=True)
    children = models.ManyToManyField(Person, related_name='+')
    married = models.BooleanField(default='FALSE')
    marriage_date = models.DateField(null=True)
    divorced = models.BooleanField(default='FALSE')
    divorce_date = models.DateField(null=True)
    notes = models.TextField(blank=True)
    current = models.BooleanField()


class Parent(models.Model):
    parent = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    biological = models.NullBooleanField(default=None) #Could change back on using booleanField if we only want yes or no 
    notes = models.TextField(blank=True)