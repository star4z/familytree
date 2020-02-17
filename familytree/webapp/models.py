from django.db import models
from django.utils.translation import gettext_lazy as _

from .submodels.location_model import Location


class Name(models.Model):
    class Prefixes(models.TextChoices):
        MR = 'Mr', _('Mr')
        MRS = 'Mrs', _('Mrs')
        MS = 'Ms', _('Ms')
        DR = 'Dr', _('Doctor')
        FIRST_LT = '1st Lt', _('First Lieutenant')
        ADM = 'Adm', _('Admiral')
        ATTY = 'Atty', _('Attorney')
        BROTHER = 'Brother', _('Brother (religious)')
        CAPT = 'Capt', _('Captain')
        CHIEF = 'Chief', _('Chief')
        CMDR = 'Cmdr', _('Commander')
        COL = 'Col', _('Colonel')
        DEAN = 'Dean', _('University Dean (includes Assistant and Associate)')
        ELDER = 'Elder', _('Elder (religious)')
        FATHER = 'Father', _('Father (religious)')
        GEN = 'Gen', _('General')
        GOV = 'Gov', _('Governor')
        HON = 'Hon', _(
            'Honorable (Cabinet Officer, Commissioner, Congressman, Judge, Supreme Court, United Nations US Delegate, '
            'Major, Senator, and Representative)')
        LT_COL = 'Lt Col', _('Lieutenant Colonel')
        MAJ = 'Maj', _('Major')
        MSGT = 'MSgt', _('Major/Master Sergeant')
        PRINCE = 'Prince', _('Prince')
        PROF = 'Prof', _('Professor (includes Assistant and Associate')
        RABBI = 'Rabbi', _('Rabbi (religious)')
        REV = 'Rev', _('Reverend (religious)')
        SISTER = 'Sister', _('Sister (religious)')

    prefix = models.CharField(max_length=7, choices=Prefixes.choices, blank=True, default='')
    first_name = models.TextField(default='')
    middle_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    suffix = models.CharField(max_length=6, blank=True, default='')
    person = models.ForeignKey('Person', on_delete=models.DO_NOTHING, related_name='alternate_name')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Person(models.Model):
    prefix = models.CharField(max_length=7, choices=Name.Prefixes.choices, blank=True,
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
    children = models.ManyToManyField(Person, related_name='children', blank=True)
    married = models.BooleanField(default=False)
    marriage_date = models.DateField(null=True, blank=True)
    divorced = models.BooleanField(default=False)
    divorce_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    current = models.BooleanField(default=False)

    def __str__(self):
        return ', '.join(str(person) for person in Person.objects.filter(partnerships=self))
