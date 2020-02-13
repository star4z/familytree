from django.db import models
from .submodels.location_model import Location

prefix_choices = tuple()


class Name(models.Model):
    prefix = models.CharField(max_length=7, choices=prefix_choices, blank=True, default='')
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Person(models.Model):
    prefix = models.CharField(max_length=7, choices=prefix_choices, blank=True,
                              default='')
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')

    preferred_name = models.TextField(blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_location = models.ForeignKey(Location, related_name="birth_location", blank=True, on_delete=models.DO_NOTHING,
                                       null=True)
    death_location = models.ForeignKey(Location, related_name="death_location", blank=True, on_delete=models.DO_NOTHING,
                                       null=True)

    living = models.BooleanField(default=True)
    gender = models.CharField(max_length=100, default='')  # Should gender be optional?
    notes = models.TextField(blank=True, default='')
    occupations = models.TextField(blank=True, default='')
    partnerships = models.ManyToManyField('Partnership', blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Partnership(models.Model):
    children = models.ManyToManyField(Person, related_name='children', null=True)
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank=True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    current = models.BooleanField(default=False)

    def __str__(self):
        return ', '.join(str(person) for person in Person.objects.filter(partnerships=self))
