from django.urls import path, include

from accounts import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup_view),
]
