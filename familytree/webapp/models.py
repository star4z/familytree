from django.db import models


class Name(models.Model):
    # Needs either some parsing or more fields for better lookup and display
    name = models.TextField()
    nickname = models.TextField()
    alternate_name = models.TextField()


class Person(models.Model):
    name = models.OneToOneField(Name, on_delete=models.CASCADE)
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
    partner = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='+')
    children = models.ManyToManyField('Person', related_name='+')
    married = models.BooleanField()
    marriage_date = models.DateField()
    divorced = models.BooleanField()
    divorce_date = models.DateField()
    notes = models.TextField()
    current = models.BooleanField()


class Parent(models.Model):
    parent = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='+')
    biological = models.BooleanField()