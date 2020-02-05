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

class Location(models.Model):
    city = models.CharField(verbose_name='city/town/village', max_length=50)
    state = models.CharField(verbose_name='state/province/region', 
        max_length=50)
    country = models.CharField(max_length=50)

class Person(models.Model):
    name = models.OneToOneField(LegalName, on_delete=models.CASCADE)
    preferred_name = models.TextField()
    birth_date = models.DateField()
    death_date = models.DateField()
    birth_location = models.OneToOneField(Location, on_delete=models.CASCADE)
    death_location = models.OneToOneField(Location, on_delete=models.CASCADE)
    living = models.BooleanField()
    gender = models.CharField(max_length=100)
    notes = models.TextField()
    occupations = models.TextField()
    partnerships = models.ManyToManyField('Partnership')
    parents = models.ManyToManyField('Parent')


class Partnership(models.Model):
    partner = models.ForeignKey(Person, on_delete=models.DO_NOTHING, 
        related_name='+', null=True)
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
