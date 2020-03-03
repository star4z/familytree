from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from webapp.models import Person, Partnership, Location
from webapp.forms import AddPersonForm, NameForm, AddLocationForm
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST

def add_person(request):
    # if this is a POST request we need to process the form data
    name_form = NameForm(request.POST)
    person_form = AddPersonForm(request.POST)

    context = {
        'name_form': name_form, 
        'person_form': person_form
    }

    if request.method == 'POST':
        # check whether it's valid:
        if all((person_form.is_valid(), name_form.is_valid())):
            created_legal_name = name_form.save(commit=False)
            
            created_person = person_form.save(commit=False)
            created_person.legal_name = created_legal_name

            created_legal_name.save()
            created_person.save()
            # redirect to a new URL:
            return redirect('person_detail', pk=created_person.id)
    # if a GET (or any other method) we'll create a blank form
    else:
        name_form = NameForm()
        person_form = AddPersonForm()
            
    return render(request, 'webapp/add_person.html', context)

# View that creates and saves a Location instance in the DB 
# based on user's input in the Add Location form
def add_location(request):
    location_form = AddLocationForm(request.POST)

    context = {
        'location_form': location_form
    }

    if request.method == 'POST':
        if location_form.is_valid():
            created_location = location_form.save(commit=False)
            created_location.save()
            return redirect('index')
        else:
            form = AddLocationForm(request.POST)

    return render(request, 'webapp/add_location.html', context)


@require_POST
def delete_person(request, pk):
    query = Person.objects.get(pk=pk)
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
