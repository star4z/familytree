import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.utils.translation import gettext_lazy as _

from .submodels.location_model import Location


class Tree(models.Model):
    title = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    authorized_users = models.ManyToManyField(User, related_name='authorized_users', blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'[{self.id}] {self.title}'

    def get_absolute_url(self):
        # Returns the url to access a Tree instance
        return reverse('tree_detail', args=[str(self.id)])


class Name(models.Model):
    prefix = models.CharField(max_length=7, blank=True, default='')
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'[{self.id}] {self.first_name} {self.last_name}'

    class Meta:
        abstract = True


class LegalName(Name):
    pass


class AlternateName(Name):
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='alternate_name')


class Person(models.Model):
    LIVING_CHOICES = [
        ('Alive', 'Alive'),
        ('Dead', 'Dead'),
        ('Unknown', 'Unknown')
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Intersex', 'Intersex'),
        ('Other', 'Other'),
        ('Unknown', 'Unknown')
    ]

    legal_name = models.OneToOneField('LegalName', on_delete=models.CASCADE, related_name='legal_name', default='')
    preferred_name = models.TextField(blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_location = models.ForeignKey(Location, related_name="birth_location", on_delete=models.DO_NOTHING, null=True,
                                       blank=True)
    death_location = models.ForeignKey(Location, related_name="death_location", on_delete=models.DO_NOTHING, null=True,
                                       blank=True)
    living = models.TextField(choices=LIVING_CHOICES, default='Unknown')
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
    partnerships = models.ManyToManyField('Partnership', blank=True, through='PersonPartnership')
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['birth_date']

    def clean(self):
        if self.birth_date and self.death_date and self.birth_date > self.death_date:
            raise ValidationError(_('Birth date may not be after death date.'))

    def __repr__(self):
        return repr(self.legal_name)

    def __str__(self):
        return str(self.legal_name)

    def get_absolute_url(self):
        # Returns the url to access a Person instance
        return reverse('person_detail', args=[str(self.id)])

    def get_generation(self, offset=0):
        if offset < -1:
            last_gen_partnership_ids = self.get_generation(offset + 1).values('partnerships')
            last_gen_partnerships = Partnership.objects.filter(pk__in=last_gen_partnership_ids)
            return Person.objects.filter(pk__in=last_gen_partnerships.values('children'))
        elif offset == -1:
            return Person.objects.filter(pk__in=self.partnerships.values('children'))
        elif offset == 0:
            return self
        elif offset == 1:
            return Partnership.objects.filter(children=self)
        else:
            return Partnership.objects.filter(
                children__in=Person.objects.filter(partnerships__in=self.get_generation(offset - 1)))

    def parents(self):
        return self.get_generation(1)

    def siblings(self):
        parents = Partnership.objects.filter(children=self)
        # need ID's from intermediate model to filter Persons
        parents_children_ids = Partnership.children.through.objects.filter(partnership__in=parents).values('person_id')
        return Person.objects.filter(pk__in=parents_children_ids).exclude(pk=self.pk)

    class IllegalAgeError(ValidationError):
        def __init__(self):
            self.message = 'Invalid '

    def age(self):
        if self.birth_date:
            if self.living:
                return relativedelta(datetime.date.today(), self.birth_date)
            elif self.death_date:
                return relativedelta(self.death_date, self.birth_date)
            else:
                raise self.IllegalAgeError()
        else:
            raise self.IllegalAgeError()


class Partnership(models.Model):
    children = models.ManyToManyField(Person, related_name='children', blank=True)
    marriage_date = models.DateField(null=True, blank=True)
    divorce_date = models.DateField(null=True, blank=True)

    # TODO: remove MaritalStatus and rename
    class MaritalStatuses(models.TextChoices):
        MARRIED = 'Married', _('Married')
        PARTNERED = 'Partnered', _('Partnered')
        LEGALLY_SEPARATED = 'Legally separated', _('Legally Separated')
        DIVORCED = 'Divorced', _('Divorced')

    marital_status = models.CharField(max_length=25, choices=MaritalStatuses.choices, default=MaritalStatuses.MARRIED)

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

    def max_death_date(self):
        return Person.objects.exclude(pk=self.pk) \
            .filter(partnerships=self, death_date__isnull=False) \
            .aggregate(Max('death_date'))['death_date__max']


class PersonPartnership(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    partnership = models.ForeignKey('Partnership', on_delete=models.CASCADE)

    def __str__(self):
        return ''
