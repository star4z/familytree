from django.shortcuts import render
from django.views import generic
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

class PersonListView(generic.ListView):
	model = Person
	paginate_by = 10

class PartnershipListView(generic.ListView):
	model = Partnership
	paginate_by = 10

"""
	 def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context
"""
