"""
URL routing for the `frontend` app.

Two route groups:

1. HTML pages — auto-glob every `*.html` in `templates/` (unchanged behavior).
2. JSON API at /api/ — DRF DefaultRouter, added in this iteration.
"""
from pathlib import Path

from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .api import EmployeeViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'employees', EmployeeViewSet, basename='employee')

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

urlpatterns = [
    path('api/', include(router.urls)),
]

for html in TEMPLATE_DIR.glob("*.html"):
    name = html.stem
    page_view = TemplateView.as_view(template_name=html.name)
    if name == "index":
        urlpatterns.append(path("", page_view, name="index"))
        urlpatterns.append(path("index.html", page_view))
    else:
        # All three forms work: clean, .html, and .html/
        urlpatterns.append(path(f"{name}/", page_view, name=name))
        urlpatterns.append(path(f"{name}.html", page_view))
        urlpatterns.append(path(f"{name}.html/", page_view))
