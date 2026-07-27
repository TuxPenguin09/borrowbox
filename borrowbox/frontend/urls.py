from pathlib import Path
from django.urls import path
from . import views
from django.views.generic import TemplateView

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

urlpatterns = []

for html in TEMPLATE_DIR.glob("*.html"):
    name = html.stem

    view = TemplateView.as_view(template_name=html.name)

    if name == "index":
        # index is always the home
        urlpatterns.append(path("", view, name="index"))
        urlpatterns.append(path("index.html", view))
    else:
        # .html included
        urlpatterns.append(path(f"{name}/", view, name=name))
        urlpatterns.append(path(f"{name}.html", view))