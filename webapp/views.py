from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from webapp.models import Person, Partnership, Location, LegalName, AlternateName
from webapp.forms import AddPersonForm, AddNameForm, AddLocationForm, AddPartnershipForm, AlternateNameForm
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST
from django.forms import modelformset_factory
from django.forms import inlineformset_factory


def add_person(request):
    AlternateNameFormSet = inlineformset_factory(Person, AlternateName, form=AlternateNameForm, extra=5, can_delete=True)
    person = Person()
    if request.method == 'POST':
        # if this is a POST request we need to process the form data
        name_form = AddNameForm(request.POST)
        person_form = AddPersonForm(request.POST, instance=person)
        alt_name_formset = AlternateNameFormSet(request.POST, instance=person)
        birth_location_form = AddLocationForm(request.POST, prefix="birth_location")
        death_location_form = AddLocationForm(request.POST, prefix="death_location")

        # Tuple that contains validation status of each filled form
        form_validations = (
            person_form.is_valid(),
            name_form.is_valid(),
            alt_name_formset.is_valid(),
            birth_location_form.is_valid(),
            death_location_form.is_valid()
        )

        # check whether it's valid:
        if all(form_validations):
            # Create a Legal Name instance from name form's data
            created_legal_name = name_form.save(commit=False)
            created_legal_name.save()

            # Create a Person instance from person form's data
            # Person instance's Legal Name attribute will be a foreign key
            created_person = person_form.save(commit=False)
            created_person.legal_name = created_legal_name
            created_person.save()

            # Create Alternate Name for person
            alt_names=alt_name_formset.save(commit=False)
            for alt_name in alt_names:
                alt_name.person_id = created_person.id
                alt_name.save()

            # Check each location form's data and query for existing Location
            # instances.
            # If location exists, stores it in the corresponding location
            # variable and sets location_created boolean to false
            # If it doesn't exist, create a new instance from form's data and
            # set location_created boolean to true
            birth_location, birth_location_created = Location.objects.get_or_create(**birth_location_form.cleaned_data)
            death_location, death_location_created = Location.objects.get_or_create(**death_location_form.cleaned_data)

            # if new location instances were created, save them in the DB
            if birth_location_created:
                birth_location.save()

            if death_location_created:
                death_location.save()

            # Assign the location instances as keys in Person instance
            created_person.birth_location = birth_location
            created_person.death_location = death_location

            created_person.save()

            # redirect to page containing new Person instance's details
            return redirect('person_detail', pk=created_person.id)

    # if a GET (or any other method) we'll create a blank form
    else:
        name_form = AddNameForm()
        person_form = AddPersonForm(instance=person)
        alt_name_formset = AlternateNameFormSet(instance=person)
        birth_location_form = AddLocationForm(prefix="birth_location")
        death_location_form = AddLocationForm(prefix="death_location")

    context = {
        'name_form': name_form,
        'person_form': person_form,
        'alt_name_formset': alt_name_formset,
        'birth_location_form': birth_location_form,
        'death_location_form': death_location_form
    }

    return render(request, 'webapp/add_person.html', context)


def add_partnership(request):
    partnership_form = AddPartnershipForm(request.POST)

    context = {
        'partnership_form': partnership_form
    }

    if request.method == 'POST':
        if partnership_form.is_valid():
            created_location = partnership_form.save(commit=False)
            created_location.save()
            return redirect('index')
        else:
            form = AddLocationForm(request.POST)

    return render(request, 'webapp/add_partnership.html', context)


@require_POST
def delete_person(request, person_pk, name_pk):
    query = Person.objects.get(pk=person_pk)
    query.delete()
    query = LegalName.objects.get(pk=name_pk)
    query.delete()
    return redirect('person')


def index(request):
    # Generate counts of person
    num_person = Person.objects.all().count()
    num_partnerships = Partnership.objects.all().count()
    context = {
        'num_person': num_person,
        'num_partnerships': num_partnerships,
    }
    return render(request, 'index.html', context=context)


class PersonListView(generic.ListView):
    model = Person
    paginate_by = 10


class PartnershipListView(generic.ListView):
    model = Partnership
    paginate_by = 10


class PersonDetailView(generic.DetailView):
    model = Person


'''
class LocationCreateView(CreateView):
    model = Location
    fields = '__all__'
'''
