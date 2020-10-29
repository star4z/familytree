from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.views.decorators.http import require_POST, require_GET

from commons.gedcom import gedcom_generator
from commons.gedcom.gedcom_parsing import parse_file
from commons.models import Tree, Person, Partnership, PersonEvent
from webapp.forms import AddPersonForm, AddNameForm, AddTreeForm, AddPartnershipForm, AlternateNameFormSet, \
    NewPartnerFormSet, PartnershipChildFormSet, UploadFileForm, EventFormSet, EventForm
from webapp.graphs import Graph
from webapp.models import Location


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
def edit_tree(request, pk):
    current_tree = Tree.objects.get(pk=pk)

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

        return render(request, 'webapp/edit_tree.html', {'tree_form': tree_form})

    else:
        raise Http404


@login_required
def save_person(request, current_tree, template_name, current_person: Person = None):
    if current_tree.creator == request.user:
        name_form = None
        person_form = None
        alt_name_formset = None
        event_form = None
        event_formset = None

        if request.method == 'POST':
            # if this is a POST request we need to process the form data
            name_form = AddNameForm(request.POST, instance=current_person.legal_name if current_person else None)
            person_form = AddPersonForm(request.POST, instance=current_person)

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

                if not current_person:
                    # Create a Person instance from person form's data
                    # Person instance's Legal Name attribute will be a foreign key
                    current_person = person_form.save(commit=False)
                    current_person.tree = current_tree
                    current_person.legal_name = created_legal_name
                    current_person.save()

                # Create Alternate Name for person
                alt_name_formset = AlternateNameFormSet(request.POST, instance=current_person)
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
                current_person.birth_location = birth_location
                current_person.death_location = death_location

                current_person.save()

                # redirect to back to the Tree detail page that
                # Person was created in
                return redirect('tree_detail', pk=current_person.tree.id)

        # if a GET (or any other method) we'll create a blank form
        if current_person:
            name_form = name_form or AddNameForm(instance=current_person.legal_name)
            initial_data = dict()
            if current_person.birth_location:
                initial_data.update({
                    'birth_city': current_person.birth_location.city,
                    'birth_state': current_person.birth_location.state,
                    'birth_country': current_person.birth_location.country,
                })
            if current_person.death_location:
                initial_data.update({
                    'death_city': current_person.death_location.city,
                    'death_state': current_person.death_location.state,
                    'death_country': current_person.death_location.country
                })
            person_form = person_form or AddPersonForm(instance=current_person, initial=initial_data)
            alt_name_formset = alt_name_formset or AlternateNameFormSet()
        else:
            name_form = name_form or AddNameForm()
            person_form = person_form or AddPersonForm()
            alt_name_formset = alt_name_formset or AlternateNameFormSet()

        context = {
            'name_form': name_form,
            'person_form': person_form,
            'alt_name_formset': alt_name_formset,
            'event_form': event_form or EventForm(),
            'event_formset': event_formset or EventFormSet(),
            'event_types': [choice[0] for choice in PersonEvent.Type.choices]
        }

        return render(request, template_name, context)

    else:
        raise Http404


@login_required
def add_person(request, pk):
    current_tree = Tree.objects.get(pk=pk)

    return save_person(request, current_tree, 'webapp/add_person.html')


@login_required
def edit_person(request, pk):
    current_person = Person.objects.get(pk=pk)
    current_tree = current_person.tree

    return save_person(request, current_tree, 'webapp/edit_person.html', current_person)


@login_required
def save_partnership(request, current_tree, template, current_partnership=None):
    tree_pk = current_tree.pk
    # Allow tree to be accessed and modified through forms if tree's creator
    # is the requesting user
    if current_tree.creator == request.user:
        partnership_form = None
        person_partner_formset = None
        partnership_child_formset = None

        if request.method == 'POST':
            partnership_form = AddPartnershipForm(data=request.POST)

            if partnership_form.is_valid():
                # Create the partnership from the form data, connect it to
                # the tree it belongs in, and save it.
                if not current_partnership:
                    current_partnership = partnership_form.save(commit=False)
                    current_partnership.tree = current_tree
                    current_partnership.save()

                    # Save the partnership's many-to-many relationships to reflect
                    # change to connected objects
                    partnership_form.save_m2m()

                # Formset for adding partner (Person) to Partnership
                person_partner_formset = NewPartnerFormSet(
                    data=request.POST,
                    instance=current_partnership,
                    form_kwargs={'tree_id': tree_pk},
                    prefix="person_partner"
                )

                # Save every added partner to reflect change.
                if person_partner_formset.is_valid():
                    people = person_partner_formset.save(commit=False)
                    for person in people:
                        person.save()

                # Add child (Person) to Partnership
                partnership_child_formset = PartnershipChildFormSet(
                    data=request.POST, instance=current_partnership,
                    form_kwargs={'tree_id': tree_pk},
                    prefix="partnership_child"
                )

                # Save every added child to reflect change
                if partnership_child_formset.is_valid():
                    children = partnership_child_formset.save(commit=False)
                    for person in children:
                        person.save()

                # redirect to back to the Tree detail page that
                # Person was created in
                return redirect('tree_detail', pk=tree_pk)

        # If request isn't POST, display forms with empty fields.
        if current_partnership:
            partnership_form = partnership_form or AddPartnershipForm(instance=current_partnership)
            person_partner_formset = person_partner_formset or NewPartnerFormSet(
                instance=current_partnership,
                form_kwargs={'tree_id': tree_pk},
                prefix="person_partner"
            )
            partnership_child_formset = partnership_child_formset or PartnershipChildFormSet(
                instance=current_partnership,
                form_kwargs={'tree_id': tree_pk},
                prefix="partnership_child"
            )
        else:
            partnership_form = partnership_form or AddPartnershipForm()
            person_partner_formset = person_partner_formset or NewPartnerFormSet(
                form_kwargs={'tree_id': tree_pk},
                prefix="person_partner"
            )
            partnership_child_formset = partnership_child_formset or PartnershipChildFormSet(
                form_kwargs={'tree_id': tree_pk},
                prefix="partnership_child")

        context = {
            'partnership_form': partnership_form,
            'person_partner_formset': person_partner_formset,
            'partnership_child_formset': partnership_child_formset
        }

        return render(request, template, context)

    else:
        raise Http404


@login_required
def add_partnership(request, pk):
    current_tree = Tree.objects.get(pk=pk)
    return save_partnership(request, current_tree, 'webapp/add_partnership.html')


@login_required
def edit_partnership(request, pk):
    current_partnership = Partnership.objects.get(pk=pk)
    current_tree = current_partnership.tree
    return save_partnership(request, current_tree, 'webapp/edit_partnership.html', current_partnership)


@login_required
@require_POST
def delete_person(request, pk):
    person_obj = Person.objects.get(pk=pk)
    alt_name_list = person_obj.alternate_name.all()
    alt_name_list.delete()
    person_obj.delete()
    query = person_obj.legal_name
    query.delete()
    return redirect('tree_detail', pk=person_obj.tree.pk)


@login_required
@require_POST
def delete_partnership(request: WSGIRequest, pk):
    partnership_obj = Partnership.objects.get(pk=pk)
    partnership_obj.delete()
    return redirect('tree_detail', pk=partnership_obj.tree.pk)


@login_required
@require_POST
def delete_tree(request, pk):
    tree = Tree.objects.get(pk=pk)
    people = Person.objects.filter(tree=tree)
    for person in people:
        delete_person(request, person.id)
    partnerships = Partnership.objects.filter(tree=tree)
    partnerships.delete()
    tree.delete()
    return redirect('tree')


def index(request):
    if request.user.is_authenticated:
        return redirect('tree')
    else:
        return redirect('/accounts/signup')


class TreeListView(LoginRequiredMixin, generic.ListView):
    model = Tree
    paginate_by = 10
    ordering = ['id']
    template_name = 'webapp/tree_list.html'
    context_object_name = 'tree_list'

    # Get Tree object only under the current user
    def get_queryset(self):
        return Tree.objects.filter(creator=self.request.user)


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
    template_name = 'webapp/tree_detail.html'

    # This is to get Person list under the specific tree to show. PersonListView class is replaced with this.
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TreeDetailView, self).get_context_data(**kwargs)
        # Add extra context from another model
        context['persons'] = Person.objects.filter(tree_id=self.kwargs['pk'])
        context['partnerships'] = Partnership.objects.filter(tree_id=self.kwargs['pk'])
        return context

    # Get Tree object only under the current user
    def get_queryset(self):
        return super(TreeDetailView, self).get_queryset().filter(creator=self.request.user).select_related('creator')


class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    model = Person
    template_name = 'webapp/person_detail.html'

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

    width = max(node.x for node in graph.nodes) + graph.padding
    height = max(node.y for node in graph.nodes) + graph.padding

    context = {
        'person': person,
        'data': graph.to_dict(),
        'width': width,
        'height': height,
    }
    return render(request, 'webapp/person_graph.html', context)


@login_required
def import_gedcom(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            parse_file(request.FILES['file'], request.user, form.cleaned_data['title'])
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request, 'webapp/tree_import.html', {'form': form})


@login_required
@require_GET
def export_gedcom(request, pk):
    tree = Tree.objects.get(pk=pk, creator=request.user)
    text_body = gedcom_generator.generate_file(tree).to_gedcom_string(recursive=True)
    response = HttpResponse(text_body, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{tree.title}.ged"'
    return response
