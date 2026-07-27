"""
URL configuration for borrowbox project.

- /admin/   – Django admin
- /api/     – DRF browsable API + JSON
- /         – frontend HTML pages (delegated to frontend.urls)
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
]