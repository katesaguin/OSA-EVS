from django.shortcuts import render, redirect
from .models import Student, Ticket
from datetime import datetime

#import login_required

# Create your views here.
def dashboard_view(request):
    current_month = datetime.now().month
    month_name = datetime(1900, current_month, 1).strftime('%B')
    tickets = Ticket.objects.all()
    students = Student.objects.all()
    id_violation = Ticket.objects.filter(id_violation=True).count()
    dress_code_violation = Ticket.objects.filter(dress_code_violation=True).count()
    uniform_violation = Ticket.objects.filter(uniform_violation=True).count()
    return render(request, 'system/dashboard.html', {
        'id_violation': id_violation,
        'uniform_violation': uniform_violation,
        'dress_code_violation': dress_code_violation,
        'month': month_name,
        'tickets': tickets,
        'students': students
    })

#@login_required (ALL FUNCTION)
def violation_views(request):
    return render(request, 'system/tickets.html')

def tally_views(request):
    return render(request, 'system/tally.html')

def statistics_view(request):
    return render(request, 'system/statistics.html')

def settings_views(request):
    return render(request, 'system/settings.html')

def ticketDetails_views(request):
    return render(request, 'system/ticket-details.html')