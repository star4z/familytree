"""familytree URL Configuration

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
from django.contrib import admin
from django.urls import include, path
# Use to redirect root view to only app: webapp (Can be changed)
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webapp/', include('webapp.urls')),
    path('', RedirectView.as_view(url='webapp/', permanent=True)),
    path('accounts/', include('accounts.urls'))
]

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings  # noqa: E402
from django.conf.urls.static import static  # noqa: E402

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
