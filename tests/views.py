from django.shortcuts import render

def tests(request):
    return render(request, 'account.html')