from django.shortcuts import render
from webapp.models import Person, Partnership
# create views here

def index(request):
	# Generate counts of person
	num_person = Person.objects.all().count()
	num_partnerships = Partnership.objects.all().count()

	context = {
		'num_person': num_person,
		'num_partnerships': num_partnerships,
	}

	return render(request, 'index.html', context=context)