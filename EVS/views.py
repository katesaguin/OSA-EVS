from django.shortcuts import render, redirect
from .models import Ticket
from django.core.paginator import Paginator
#import login_required

# Create your views here.
def dashboard_view(request):
    return render(request, 'system/dashboard.html')

#@login_required (ALL FUNCTION)
def violation_views(request):
    tickets = Ticket.objects.all().order_by('-date_created')
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'system/tickets.html', context)

def tally_views(request):
    return render(request, 'system/tally.html')

def statistics_view(request):
    return render(request, 'system/statistics.html')

def settings_views(request):
    return render(request, 'system/settings.html')

def ticketDetails_views(request):
    return render(request, 'system/ticket-details.html')