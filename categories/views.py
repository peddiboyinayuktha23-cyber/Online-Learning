from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError

from .models import Category


def categories_page(request):
    try:
        categories = list(Category.objects.filter(is_active=True))
    except (OperationalError, ProgrammingError):
        categories = []
    context = {'categories': categories}
    return render(request, 'categories/categories.html', context)
