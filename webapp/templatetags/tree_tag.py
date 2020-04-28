from django import template
from webapp.models import Tree
from django.core.paginator import Paginator
register = template.Library()


@register.inclusion_tag('webapp/sidebar_tree_list.html', takes_context=True)
def render_recent_trees(context):
    request = context['request']

    sidebar_tree_list = Tree.objects.filter(creator=request.user).order_by("id")
    paginator = Paginator(sidebar_tree_list, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sidebar_tree_list': sidebar_tree_list,
        'page_obj': page_obj
    }
    return context
