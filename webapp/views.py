from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.views.decorators.http import require_POST

from webapp.forms import AddPersonForm, AddNameForm, AddTreeForm, AddPartnershipForm, AlternateNameFormSet, PersonFormSet, PartnershipChildFormSet
from webapp.graphs import Graph
from webapp.models import Person, Partnership, Location, LegalName, Tree


@login_required
def add_tree(request):
    # If request is POST, create and save Tree from valid form's values and 
    # assign the current user as the tree's creator.
    if request.method == 'POST':
        tree_form = AddTreeForm(request.POST)

        current_user = request.user
        if tree_form.is_valid():
            created_tree = tree_form.save(commit=False)
            created_tree.save()

            created_tree.creator = current_user
            created_tree.save()
            
            # Redirect to the Tree's details page after a valid creation.
            return redirect('tree_detail', pk=created_tree.id)

    # If request is not POST, display an empty form for creating a Tree
    else:
        tree_form = AddTreeForm()

    return render(request, 'webapp/add_tree.html', {'tree_form': tree_form})

@login_required
def edit_tree(request, tree_pk):
    current_tree = Tree.objects.get(pk=tree_pk)

    # Check that the current user is the creator of this Tree before they
    # can modify it
    if current_tree.creator == request.user:
        # If request is POST, update and save the Tree from valid form's values
        if request.method == 'POST':
            tree_form = AddTreeForm(request.POST, instance=current_tree)

            if tree_form.is_valid():
                tree_form.save()

                return redirect('tree_detail', pk=current_tree.id)
        # If request is not POST, show an empty form for updating the Tree
        else:
            tree_form = AddTreeForm(instance=current_tree)

        return render(request, 'webapp/add_tree.html', {'tree_form': tree_form})

    else:
        raise Http404


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

            # Create/Save instances if all forms are valid.
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
def edit_person(request, tree_pk, person_pk):
    current_tree = Tree.objects.get(pk=tree_pk)
    current_person = Person.objects.get(pk=person_pk)

    # User validation to prevent other users from adding to trees that aren't theirs
    if current_tree.creator == request.user:
        if request.method == 'POST':
            # if this is a POST request we need to process the form data
            name_form = AddNameForm(request.POST, instance=current_person.legal_name)
            person_form = AddPersonForm(request.POST, instance=current_person)

            # Tuple that contains validation status of each filled form
            form_validations = (
                person_form.is_valid(),
                name_form.is_valid(),
            )

            # Update/Save instances if all forms are valid.
            if all(form_validations):

                name_form.save()
                person_form.save()

                alt_name_formset = AlternateNameFormSet(request.POST, instance=current_person)
                if alt_name_formset.is_valid():
                    alt_name_formset.save()

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
                current_person.birth_location = birth_location
                current_person.death_location = death_location

                current_person.save()

                # redirect to page containing new Person instance's details
                return redirect('person_detail', pk=current_person.id)

        # if a GET (or any other method) we'll create a blank form
        else:
            name_form = AddNameForm(instance=current_person.legal_name)
            person_form = AddPersonForm(instance=current_person, 
                initial={'birth_city': current_person.birth_location.city,
                        'birth_state': current_person.birth_location.state,
                        'birth_country': current_person.birth_location.country,
                        'death_city': current_person.death_location.city,
                        'death_state': current_person.death_location.state,
                        'death_country': current_person.death_location.country})
            alt_name_formset = AlternateNameFormSet(instance=current_person)

        context = {
            'name_form': name_form,
            'person_form': person_form,
            'alt_name_formset': alt_name_formset,
        }

        return render(request, 'webapp/edit_person.html', context)

    else:
        raise Http404


@login_required
def add_partnership(request, tree_pk):
    current_tree = Tree.objects.get(pk=tree_pk)

    # Allow tree to be accessed and modified through forms if tree's creator 
    # is the requesting user
    if current_tree.creator == request.user:
        if request.method == 'POST':
            partnership_form = AddPartnershipForm(data=request.POST, tree_id=tree_pk)

            if partnership_form.is_valid():
                # Create the partnership from the form data, connect it to
                # the tree it belongs in, and save it.
                created_partnership = partnership_form.save(commit=False)
                created_partnership.tree = current_tree
                created_partnership.save()

                # Save the partnership's many-to-many relationships to reflect
                # change to connected objects
                partnership_form.save_m2m()

                # Formset for adding partner (Person) to Partnership
                person_partner_formset = PersonFormSet(data=request.POST, instance=created_partnership, form_kwargs={'tree_id': tree_pk}, prefix="person_partner")
                
                # Save every added partner to reflect change.
                if person_partner_formset.is_valid():
                    people = person_partner_formset.save(commit=False)
                    for person in people:
                        person.save()

                # Add child (Person) to Partnership
                partnership_child_formset = PartnershipChildFormSet(data=request.POST, instance=created_partnership, form_kwargs={'tree_id': tree_pk}, prefix="partnership_child")
                
                # Save every added child to reflect change
                if partnership_child_formset.is_valid():
                    children = partnership_child_formset.save(commit=False)
                    for person in children:
                        person.save()
                
                return redirect('partnership')

        # If request isn't POST, display forms with empty fields.
        else:
            partnership_form = AddPartnershipForm(tree_id=tree_pk)
            person_partner_formset = PersonFormSet(form_kwargs={'tree_id': tree_pk}, prefix="person_partner")
            partnership_child_formset = PartnershipChildFormSet(form_kwargs={'tree_id': tree_pk}, prefix="partnership_child")

        context = {
            'partnership_form': partnership_form,
            'person_partner_formset': person_partner_formset,
            'partnership_child_formset': partnership_child_formset
        }

        return render(request, 'webapp/add_partnership.html',context)

    else:
        raise Http404


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


@login_required
@require_POST
def delete_partnership(request, partnership_pk, person_pk):
    partnership_obj = Partnership.objects.get(pk=partnership_pk)
    partnership_obj.delete()
    return redirect('person_detail', pk=person_pk)


@login_required
@require_POST
def delete_tree(request, tree_pk):
    tree = Tree.objects.get(pk=tree_pk)
    people = Person.objects.filter(tree=tree)
    for person in people:
        delete_person(request, person.id, person.legal_name.id, tree.id)
    partnerships = Partnership.objects.filter(tree=tree)
    partnerships.delete()
    tree.delete()
    return redirect('tree')


@login_required
@require_POST
def go_back_tree(request, tree_pk):
    return redirect('tree_detail', pk=tree_pk)


toast_messages = {
    'logged_in': (messages.SUCCESS, 'Logged in successfully. Welcome to Family Tree'),
    'password_reset': (messages.SUCCESS, 'Password reset successfully.'),
    'activation_success': (messages.SUCCESS, 'Your account was activated successfully. Welcome to Family Tree')
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

    # Get Tree object only under the current user
    def get_queryset(self):
        return super(TreeListView, self).get_queryset().filter(creator=self.request.user).select_related('creator')


# Have not integrate the partnership yet.
class PartnershipListView(LoginRequiredMixin, generic.ListView):
    model = Partnership
    paginate_by = 10
    ordering = ['id']

    def get_queryset(self):
        trees = Tree.objects.select_related('creator').filter(creator=self.request.user)
        return super(PartnershipListView, self).get_queryset().filter(tree__in=trees)


class TreeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tree

    # This is to get Person list under the specific tree to show. PersonListView class is replaced with this.
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TreeDetailView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['person_list'] = Person.objects.filter(tree_id=self.kwargs['pk'])
        return context

    # Get Tree object only under the current user
    def get_queryset(self):
        return super(TreeDetailView, self).get_queryset().filter(creator=self.request.user).select_related('creator')


class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    model = Person

    # Users can only access their own person_detail page they created
    def get_object(self, **kwargs):
        return get_object_or_404(Person, pk=self.kwargs['pk'], tree__in=Tree.objects.filter(creator=self.request.user))


def graph_person(request, pk):
    person = get_object_or_404(Person, pk=pk, tree__in=Tree.objects.filter(creator=request.user))
    graph = Graph()

    partnerships = person.partnerships.all()
    if partnerships:
        # TODO: add option to graph multiple partnerships
        for partnership in partnerships[:1]:
            graph.add_partnership(partnership, 50, 0)
            if partnership.children.exists():
                graph.add_children(partnership, depth=2)
    else:
        graph.add_person(person, 0, 0)

    if person.parents():
        graph.add_parents(person, depth=2)

    graph.normalize(extra_padding=50)

    context = {
        'person': person,
        'data': graph.to_dict()
    }
    return render(request, 'webapp/person_graph.html', context)
