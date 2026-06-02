from django.urls import path

from . import views

urlpatterns = [
    path("checkout/<slug:slug>/", views.checkout, name="payment_checkout"),
    path("success/<uuid:payment_id>/", views.payment_success, name="payment_success"),
    path("failure/<uuid:payment_id>/", views.payment_failure, name="payment_failure"),
]
