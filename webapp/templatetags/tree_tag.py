from django import template
from webapp.models import Tree
from django.core.paginator import Paginator
register = template.Library()


@register.inclusion_tag('webapp/sidebar_tree_list.html', takes_context=True)
def render_sidebar_trees(context):
    request = context['request']
    sidebar_tree_list = Tree.objects.filter(creator=request.user).order_by("id")

    paginator = Paginator(sidebar_tree_list, 5)
    trees = paginator.page(1)

    return {'trees': trees}
