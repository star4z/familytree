from django.db import models

prefix_choices = tuple()


class Name(models.Model):
    prefix = models.CharField(max_length=7, choices=prefix_choices)
    first_name = models.TextField()
    middle_name = models.TextField()
    last_name = models.TextField()
    suffix = models.CharField(max_length=6)


class LegalName(Name):
    pass


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING)


class Person(models.Model):
    name = models.OneToOneField(LegalName, on_delete=models.CASCADE)
    preferred_name = models.TextField()
    birth_date = models.DateField()
    death_date = models.DateField()
    birth_location = models.TextField() #TODO: change to location class
    death_location = models.TextField() #TODO: change to location class
    living = models.BooleanField()
    gender = models.CharField(max_length=100)
    notes = models.TextField()
    occupations = models.TextField()
    partnerships = models.ManyToManyField('Partnership')
    parents = models.ManyToManyField('Parent')


class Partnership(models.Model):
    partner = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name='+', null=True)
    children = models.ManyToManyField(Person, related_name='+')
    married = models.BooleanField()
    marriage_date = models.DateField()
    divorced = models.BooleanField()
    divorce_date = models.DateField()
    notes = models.TextField()
    current = models.BooleanField()


class Parent(models.Model):
    parent = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    biological = models.BooleanField()
    notes = models.TextField()
