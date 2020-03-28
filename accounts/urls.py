from django.urls import path, include

from accounts import views
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup_view, name="signup"),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('password_change', views.GoHomeAfterPasswordChange.as_view(), name='password_change')
]
