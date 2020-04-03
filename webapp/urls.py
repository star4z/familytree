"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

#Have to use tree_pk for some instead of pk to avoid overlapping names.
#Should add a back button of some sort on Person detail to go back to Tree detail page.
urlpatterns = [
    path('', views.index, name='index'),
    path('tree/', views.TreeListView.as_view(), name = 'tree'),
    path('partnership/', views.PartnershipListView.as_view(), name='partnership'),
    path('tree/<int:pk>/', views.TreeDetailView.as_view(), name='tree_detail'),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('person/<int:pk>/graph/', views.graph_person, name='person_graph'),
    path('person/delete/<int:person_pk>/<int:name_pk>/<int:tree_pk>/', views.delete_person, name="delete_person"),
    path('person/delete/<int:partnership_pk>/<int:person_pk>/', views.delete_partnership, name="delete_partnership"),
    path('tree/add_tree/', views.add_tree, name='add_tree'),
    path('tree/<int:tree_pk>/add_person/', views.add_person, name='add_person'),
    path('tree/<int:tree_pk>/add_partnership/', views.add_partnership, name='add_partnership'),
]
