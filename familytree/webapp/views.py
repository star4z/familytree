from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from webapp.models import Person, Partnership, Location
from webapp.forms import addPersonForm, NameForm, AddLocationForm
from django.views.generic.edit import CreateView

def addPerson(request):
    # if this is a POST request we need to process the form data
    name_form = NameForm(request.POST)
    person_form = addPersonForm(request.POST)
    if request.method == 'POST':
        # check whether it's valid:
        if all((person_form.is_valid(), name_form.is_valid())):
            profile = person_form.save(commit=False)
            lname = name_form.save(commit=False)
            lname.legal_name = profile
            lname.save()
            profile.save()
            id = profile.id
            # redirect to a new URL:
            return redirect('person_detail', pk=id)
    # if a GET (or any other method) we'll create a blank form
    else:
        name_form = NameForm()
        person_form = addPersonForm()
    return render(request, 'webapp/createPerson.html', {'name_form': name_form, 'person_form': person_form})

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