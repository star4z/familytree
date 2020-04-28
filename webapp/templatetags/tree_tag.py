from django import template
from webapp.models import Tree
register = template.Library() 

@register.inclusion_tag('webapp/sidebar_tree_list.html')
def render_recent_trees(user):
    return {
        'sidebar_tree_list': Tree.objects.filter(creator=user).order_by("id")[:5]
    }