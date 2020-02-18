from django.db import models
from django.contrib.auth.models import User
from .submodels.location_model import Location


class Tree(models.Model):
    title = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    authorized_users = models.ManyToManyField(User, related_name='authorized_users', blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.title}'


class Name(models.Model):
    prefix = models.CharField(max_length=7, blank=True, default='')
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        abstract = True


class LegalName(Name):
    pass


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='alternate_name')


class Person(models.Model):
    legal_name = models.OneToOneField('LegalName', on_delete=models.CASCADE, related_name='legal_name', blank='true',
                                      default='')

    preferred_name = models.TextField(blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_location = models.ForeignKey(Location, related_name="birth_location", blank=True, on_delete=models.DO_NOTHING,
                                       null=True)
    death_location = models.ForeignKey(Location, related_name="death_location", blank=True, on_delete=models.DO_NOTHING,
                                       null=True)

    living = models.BooleanField(default=True)
    gender = models.CharField(max_length=100, default='')  # Should gender be optional?
    partnerships = models.ManyToManyField('Partnership', blank=True)
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.legal_name.first_name} {self.legal_name.last_name}'


class Partnership(models.Model):
    children = models.ManyToManyField(Person, related_name='children', blank=True)
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank=True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return ', '.join(str(person) for person in Person.objects.filter(partnerships=self))
