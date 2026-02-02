from django.urls import path

from sas import api_views
from . import views

urlpatterns = [
    path('ispiti/', views.ispiti_list, name='ispiti_list'),
    path('ispiti/prijava/<int:termin_id>/', views.prijava_ispita, name='prijava_ispita'),
    path('ispiti/odjava/<int:termin_id>/', views.odjava_ispita, name='odjava_ispita'),
    path('finansije/', views.finansije, name='finansije'),

    # REST API
    path('api/ispiti/', api_views.api_ispiti_list, name='api_ispiti_list'),
    path('api/prijave/', api_views.api_prijave_list, name='api_prijave_list'),
    path('api/prijave/kreiraj/', api_views.api_prijava_create, name='api_prijava_create'),
    path('api/finansije/', api_views.api_finansije, name='api_finansije'),
]