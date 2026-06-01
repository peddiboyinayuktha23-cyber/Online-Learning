from django.urls import path
from . import views

urlpatterns = [
    path('', views.certifications, name='certifications'),
]