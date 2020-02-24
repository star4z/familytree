from django.db import models
from django.contrib.auth.models import User
from .submodels.location_model import Location
from django.urls import reverse  # To generate URLS by reversing URL patterns


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
        return f'[{self.id}] {self.first_name} {self.last_name}'

    class Meta:
        abstract = True


class LegalName(Name):
    pass


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='alternate_name')


class Person(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('INTERSEX', 'Intersex'),
        ('OTHER', 'Other'),
    ]

    legal_name = models.OneToOneField('LegalName', on_delete=models.CASCADE, related_name='legal_name', default='')
    preferred_name = models.TextField(blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_location = models.ForeignKey(Location, related_name="birth_location", on_delete=models.DO_NOTHING, null=True,
                                       blank=True)
    death_location = models.ForeignKey(Location, related_name="death_location", on_delete=models.DO_NOTHING, null=True,
                                       blank=True)
    living = models.BooleanField(default=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
    partnerships = models.ManyToManyField('Partnership', blank=True, through='PersonPartnership')
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'[{self.id}] {self.legal_name.first_name} {self.legal_name.last_name}'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('person_detail', args=[str(self.id)])


class Partnership(models.Model):
    children = models.ManyToManyField(Person, related_name='children', blank=True)
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank=True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def partners(self):
        return Person.objects.filter(partnerships=self)

    def partners_str(self):
        partners = self.partners()
        partners_list = ', '.join(
            f'{person.legal_name.first_name} {person.legal_name.last_name}' for person in partners)
        return partners_list if partners else '(empty)'

    def __str__(self):
        return f'[{self.id}] ' + self.partners_str()


class PersonPartnership(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    partnership = models.ForeignKey('Partnership', on_delete=models.CASCADE)

    def __str__(self):
        return ''
