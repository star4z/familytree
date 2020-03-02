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

urlpatterns = [
	path('', views.index, name='index'),
	path('person/', views.PersonListView.as_view(), name='person'),
	path('partnership/', views.PartnershipListView.as_view(), name='partnership'),
	path('person/<int:pk>', views.PersonDetailView.as_view(), name='person_detail'),
	path('add/', views.addPerson, name='add'),
	path('person/delete/<int:pk>/', views.delete_person, name="delete_person")
]
