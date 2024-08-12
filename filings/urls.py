from django.urls import path

from . import views

app_name = "filings"
urlpatterns = [
    path("search/<str:search_text>/", views.search, name="search"),
    path("query/", views.query, name="query"),
    path("filing/", views.filing, name="filing"),
    path("prompt/", views.prompt, name="prompt"),
]