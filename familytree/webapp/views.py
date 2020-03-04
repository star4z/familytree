from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from webapp.models import Person, Partnership, Location, LegalName
from webapp.forms import AddPersonForm, AddNameForm, AddLocationForm
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST

def add_person(request):
    if request.method == 'POST':
         # if this is a POST request we need to process the form data
        name_form = AddNameForm(request.POST)
        person_form = AddPersonForm(request.POST)
        birth_location_form = AddLocationForm(request.POST)
        death_location_form = AddLocationForm(request.POST)

        form_validations = (
            person_form.is_valid(), 
            name_form.is_valid(),
            birth_location_form.is_valid(), 
            death_location_form.is_valid()
        )

        # check whether it's valid:
        if all(form_validations):
            created_legal_name = name_form.save(commit=False)
            created_legal_name.save()
            
            created_person = person_form.save(commit=False)
            created_person.legal_name = created_legal_name

            birth_location, birth_location_created = Location.objects.get_or_create(**birth_location_form.cleaned_data)
            death_location, death_location_created = Location.objects.get_or_create(**death_location_form.cleaned_data)

            if birth_location_created:
                birth_location.save()

            if death_location_created:
                death_location.save()

            created_person.birth_location = birth_location
            created_person.death_location = death_location
            
            created_person.save()
            # redirect to a new URL:
            return redirect('person_detail', pk=created_person.id)

    # if a GET (or any other method) we'll create a blank form
    else:
        name_form = AddNameForm()
        person_form = AddPersonForm()
        birth_location_form = AddLocationForm()
        death_location_form = AddLocationForm()
    
    context = {
            'name_form': name_form, 
            'person_form': person_form,
            'birth_location_form': birth_location_form,
            'death_location_form': death_location_form
    }
            
    return render(request, 'webapp/add_person.html', context)


# View that creates and saves a Location instance in the DB 
# based on user's input in the Add Location form
def add_location(request):
    if request.method == 'POST':
        location_form = AddLocationForm(request.POST)

        if location_form.is_valid():
            created_location = location_form.save(commit=False)
            created_location.save()
            return redirect('index')
    else:
        location_form = AddLocationForm()
    
    context = {
        'location_form': location_form
    }

    return render(request, 'webapp/add_location.html', context)


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
