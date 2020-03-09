import datetime

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

from .submodels.location_model import Location
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.utils.translation import gettext_lazy as _


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
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Intersex', 'Intersex'),
        ('Other', 'Other'),
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

    def clean(self):
        if self.birth_date and self.death_date and self.birth_date > self.death_date:
            raise ValidationError(_('Birth date may not be after death date.'))

    def __str__(self):
        return f'[{self.id}] {self.legal_name.first_name} {self.legal_name.last_name}'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('person_detail', args=[str(self.id)])

    def get_generation(self, offset=0):
        if offset < -1:
            generation = []
            for person in self.get_generation(offset + 1):
                for partnership in person.partnerships.all():
                    generation += partnership.children.all()
            return generation
        elif offset == -1:
            return [child for partnership in self.partnerships.all() for child in partnership.children.all()]
        elif offset == 0:
            return [self]
        elif offset == 1:
            return self.parents()
        else:
            generation = []
            for partnership in self.parents():
                for partner in partnership.partners():
                    generation += partner.get_generation(offset - 1)
            return generation

    def parents(self):
        return [partnership for partnership in Partnership.objects.filter(children=self)]

    def siblings(self):
        return [child for parents in self.parents() for child in parents.children.all() if child != self]

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

    def marital_status(self):
        relationship_statuses = set()
        for partnership in self.partnerships.all():
            other_living = Person.objects.filter(partnerships=partnership, living=True).exists()
            if other_living:
                if partnership.married:
                    if partnership.divorced:
                        if partnership.current:
                            relationship_statuses.add(Partnership.MaritalStatus.PARTNERED)
                        else:
                            relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                    else:
                        if partnership.current:
                            relationship_statuses.add(Partnership.MaritalStatus.MARRIED)
                        else:
                            relationship_statuses.add(Partnership.MaritalStatus.SEPARATED)
                else:
                    if partnership.divorced:
                        # ERROR! Must marry to divorce
                        pass
                    else:
                        if partnership.current:
                            relationship_statuses.add(Partnership.MaritalStatus.PARTNERED)
                        else:
                            relationship_statuses.add(Partnership.MaritalStatus.SINGLE)
            else:
                if self.living:
                    if partnership.married:
                        if partnership.divorced:
                            relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                        else:
                            relationship_statuses.add(Partnership.MaritalStatus.WIDOWED)
                    else:
                        if partnership.divorced:
                            # Error! Must marry to divorce
                            pass
                        else:
                            if partnership.current:
                                relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                            else:
                                relationship_statuses.add(Partnership.MaritalStatus.SINGLE)
                else:
                    if partnership.married:
                        if partnership.divorced:
                            relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                            if partnership.current:
                                max_death_date = Partnership.max_death_date()
                                if self.death_date and max_death_date and self.death_date > max_death_date:
                                    relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                                else:
                                    relationship_statuses.add(Partnership.MaritalStatus.PARTNERED)
                            else:
                                relationship_statuses.add(Partnership.MaritalStatus.DIVORCED)
                        else:
                            max_death_date = partnership.max_death_date()
                            if self.death_date and max_death_date and self.death_date > max_death_date:
                                relationship_statuses.add(Partnership.MaritalStatus.WIDOWED)
                            else:
                                relationship_statuses.add(Partnership.MaritalStatus.MARRIED)
                    else:
                        if partnership.divorced:
                            # Error! Must marry to divorce
                            pass
                        else:
                            if partnership.current:
                                relationship_statuses.add(Partnership.MaritalStatus.PARTNERED)
                            else:
                                relationship_statuses.add(Partnership.MaritalStatus.SINGLE)
        # If the person has no partnerships then they are single
        if not relationship_statuses:
            relationship_statuses.add(Partnership.MaritalStatus.SINGLE)
        return max(relationship_statuses)[1]


class Partnership(models.Model):
    children = models.ManyToManyField(Person, related_name='children', blank=True)
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank=True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    tree = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True)

    def clean(self):
        if self.divorced and not self.married:
            raise ValidationError(_('Must be married to be divorced.'))
        elif self.divorce_date and self.marriage_date and self.divorce_date < self.marriage_date:
            raise ValidationError(_('Divorce must come after marriage.'))

    def partners(self):
        return Person.objects.filter(partnerships=self)

    def partners_str(self):
        partners = self.partners()
        partners_list = ', '.join(
            f'{person.legal_name.first_name} {person.legal_name.last_name}' for person in partners)
        return partners_list if partners else '(empty)'

    def __str__(self):
        return f'[{self.id}] ' + self.partners_str()

    class MaritalStatus:
        MARRIED = 5, 'Married'
        PARTNERED = 4, 'Partnered'
        SEPARATED = 3, 'Legally separated'
        WIDOWED = 2, 'Widowed'
        DIVORCED = 1, 'Divorced'
        SINGLE = 0, 'Single'

    def max_death_date(self):
        return Person.objects.exclude(pk=self.pk) \
            .filter(partnerships=self, death_date__isnull=False) \
            .aggregate(Max('death_date'))['death_date__max']


class PersonPartnership(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    partnership = models.ForeignKey('Partnership', on_delete=models.CASCADE)

    def __str__(self):
        return ''