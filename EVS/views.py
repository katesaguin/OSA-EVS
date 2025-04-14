from django.shortcuts import render, redirect
from .models import student
#import login_required

# Create your views here.
def dashboard_view(request):
    students = student.objects.all()
    return render(request, 'system/dashboard.html')

#@login_required (ALL FUNCTION)
def violation_views(request):
    return render(request, 'system/tickets.html')

def tally_views(request):
    return render(request, 'system/tally.html')

def statistics_view(request):
    return render(request, 'system/statistics.html')

def settings_views(request):
    return render(request, 'system/settings.html')
