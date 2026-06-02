from django.urls import path

from . import views

urlpatterns = [
    path("<str:certificate_id>/", views.certificate_detail, name="certificate_detail"),
    path("verify/<str:certificate_id>/", views.verify_certificate, name="verify_certificate"),
]
