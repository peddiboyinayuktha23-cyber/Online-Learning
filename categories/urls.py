from django.urls import path

from .views import categories_page

urlpatterns = [

    path('', categories_page, name='categories'),

]