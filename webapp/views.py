from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect, Http404
from webapp.models import Person, Partnership, Location, LegalName, AlternateName, Tree
from webapp.forms import AddPersonForm, AddNameForm, AddTreeForm, AddPartnershipForm, AlternateNameFormSet
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST


@login_required
def add_tree(request):
    if request.method == 'POST':
        tree_form = AddTreeForm(request.POST)
            
        current_user = request.user
        if tree_form.is_valid():
            created_tree = tree_form.save(commit=False)
            created_tree.save()

            created_tree.creator = current_user
            created_tree.save()
            
            return redirect('tree_detail', pk=created_tree.id)
    else:
        tree_form = AddTreeForm()

    return render(request, 'webapp/add_tree.html', {'tree_form': tree_form})


@login_required
def add_person(request, tree_pk):
    current_tree = Tree.objects.get(pk=tree_pk)

    # User validation to prevent other users from adding to trees that aren't theirs
    if current_tree.creator == request.user:
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
                created_legal_name.tree = current_tree
                created_legal_name.save()

                # Create a Person instance from person form's data
                # Person instance's Legal Name attribute will be a foreign key
                created_person = person_form.save(commit=False)
                created_person.tree = current_tree
                created_person.legal_name = created_legal_name
                created_person.save()

                # Create Alternate Name for person
                alt_name_formset = AlternateNameFormSet(request.POST, instance=created_person)
                if alt_name_formset.is_valid():
                    alt_names = alt_name_formset.save(commit=False)
                    for alt_name in alt_names:
                        alt_name.tree = current_tree
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

    else:
        raise Http404


@login_required
def add_partnership(request):
    if request.method == 'POST':
        partnership_form = AddPartnershipForm(request.POST, user=request.user)

        if partnership_form.is_valid():
            created_partnership = partnership_form.save(commit=False)
            created_partnership.save()

            return redirect('index')
    else:
        partnership_form = AddPartnershipForm(user=request.user)

    return render(request, 'webapp/add_partnership.html',
                  {'partnership_form': partnership_form})


@login_required
@require_POST
def delete_person(request, person_pk, name_pk, tree_pk):
    person_obj = Person.objects.get(pk=person_pk)
    alt_name_list = person_obj.alternate_name.all()
    alt_name_list.delete()
    person_obj.delete()
    query = LegalName.objects.get(pk=name_pk)
    query.delete()
    return redirect('tree_detail', pk=tree_pk)


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
    ordering = ['id']

    #Get Tree object only under the current user
    def get_queryset(self):
        return super(TreeListView, self).get_queryset().filter(creator=self.request.user).select_related('creator')

# Have not integrate the partnership yet.
class PartnershipListView(LoginRequiredMixin, generic.ListView):
    model = Partnership
    paginate_by = 10
    ordering = ['id']


class TreeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tree

    # This is to get Person list under the specific tree to show. PersonListView class is replaced with this.
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TreeDetailView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['person_list'] = Person.objects.filter(tree_id=self.kwargs['pk'])
        return context

    #Get Tree object only under the current user
    def get_queryset(self):
        return super(TreeDetailView, self).get_queryset().filter(creator=self.request.user).select_related('creator')

class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    model = Person

    # Users can only access their own person_detail page they created
    def get_object(self):
        trees = Tree.objects.filter(creator=self.request.user).select_related('creator')
        get_person = get_object_or_404(Person, pk=self.kwargs['pk'])
        for tree in trees:
            get_tree = tree
            if get_person.tree == get_tree:
                return Person.objects.get(tree=get_tree, pk=self.kwargs['pk'])
        raise Http404