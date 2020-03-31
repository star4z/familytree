from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import generic
from django.views.decorators.http import require_POST

from webapp.forms import AddPersonForm, AddNameForm, AddTreeForm, AddPartnershipForm, AlternateNameFormSet
from webapp.graph import Graph
from webapp.models import Person, Partnership, Location, LegalName, Tree, PersonPartnership


@login_required
def add_tree(request):
    if request.method == 'POST':
        tree_form = AddTreeForm(request.POST)

        if tree_form.is_valid():
            created_tree = tree_form.save(commit=False)
            created_tree.save()

            return redirect('tree_detail', pk=created_tree.id)
    else:
        tree_form = AddTreeForm()

    return render(request, 'webapp/add_tree.html', {'tree_form': tree_form})


@login_required
def add_person(request):
    if request.method == 'POST':
        # if this is a POST request we need to process the form data
        name_form = AddNameForm(request.POST)
        person_form = AddPersonForm(request.POST)

        # Tuple that contains validation status of each filled form
        form_validations = (
            person_form.is_valid(),
            name_form.is_valid(),
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
            alt_name_formset = AlternateNameFormSet(request.POST, instance=created_person)
            if alt_name_formset.is_valid():
                alt_names = alt_name_formset.save(commit=False)
                for alt_name in alt_names:
                    alt_name.save()

            # Check each location form's data and query for existing Location
            # instances.
            # If location exists, stores it in the corresponding location
            # variable and sets location_created boolean to false
            # If it doesn't exist, create a new instance from form's data and
            # set location_created boolean to true
            birth_location, birth_loc_was_created = Location.objects.get_or_create(
                city=person_form.cleaned_data['birth_city'],
                state=person_form.cleaned_data['birth_state'],
                country=person_form.cleaned_data['birth_country'])

            death_location, death_loc_was_created = Location.objects.get_or_create(
                city=person_form.cleaned_data['death_city'],
                state=person_form.cleaned_data['death_state'],
                country=person_form.cleaned_data['death_country'])

            # if new location instances were created, save them in the DB
            if birth_loc_was_created:
                birth_location.save()

            if death_loc_was_created:
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
        person_form = AddPersonForm()
        alt_name_formset = AlternateNameFormSet()

    context = {
        'name_form': name_form,
        'person_form': person_form,
        'alt_name_formset': alt_name_formset,
    }

    return render(request, 'webapp/add_person.html', context)


@login_required
def add_partnership(request):
    if request.method == 'POST':
        partnership_form = AddPartnershipForm(request.POST)

        if partnership_form.is_valid():
            created_partnership = partnership_form.save(commit=False)
            created_partnership.save()

            return redirect('index')
    else:
        partnership_form = AddPartnershipForm()

    return render(request, 'webapp/add_partnership.html',
                  {'partnership_form': partnership_form})


@login_required
@require_POST
def delete_person(request, person_pk, name_pk):
    person_obj = Person.objects.get(pk=person_pk)
    alt_name_list = person_obj.alternate_name.all()
    alt_name_list.delete()
    person_obj.delete()
    query = LegalName.objects.get(pk=name_pk)
    query.delete()
    return redirect('person')


toast_messages = {
    'logged_in': (messages.SUCCESS, 'Logged in successfully. Welcome to Family Tree'),
    'password_reset': (messages.SUCCESS, 'Password reset successfully.'),
}


def index(request):
    # Generate counts of Tree, Person, and Partnership
    num_tree = Tree.objects.all().count()
    num_person = Person.objects.all().count()
    num_partnerships = Partnership.objects.all().count()
    context = {
        'num_tree': num_tree,
        'num_person': num_person,
        'num_partnerships': num_partnerships,
    }

    message = request.GET.get('message')
    if message and message in toast_messages:
        messages.add_message(request, *toast_messages[message])
        # Redirect to remove message parameter from url
        return redirect('/webapp/')

    return render(request, 'index.html', context=context)


class TreeListView(LoginRequiredMixin, generic.ListView):
    model = Tree
    paginate_by = 10


class PersonListView(LoginRequiredMixin, generic.ListView):
    model = Person
    paginate_by = 10
    ordering = ['id']


class PartnershipListView(LoginRequiredMixin, generic.ListView):
    model = Partnership
    paginate_by = 10
    ordering = ['id']


class TreeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tree


class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    model = Person


def graph_person(request, pk):
    person = Person.objects.get(pk=pk)

    graph = Graph()

    graph.add_person(person, 100, 100)

    context = {
        'data': graph.to_json()
    }
    return render(request, 'webapp/person_graph.html', context)
