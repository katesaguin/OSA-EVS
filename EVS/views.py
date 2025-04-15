from django.shortcuts import render, redirect
from .models import Student, Ticket, TicketReason, Reason, AcademicYear
from datetime import datetime
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
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

@ensure_csrf_cookie
def ticketDetails_views(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    student = Student.objects.get(student_id=ticket.student.student_id)
    reasons = Reason.objects.all()
    selected_reason_ids = TicketReason.objects.filter(ticket_id=ticket_id).values_list('reason_id', flat=True)
    return render(request, 'system/ticket-details.html', {
        'ticket': ticket,
        'student': student,
        'reasons': reasons,
        'selected': selected_reason_ids
    })

def clear_violation(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    ticket.ticket_status = 2
    ticket.date_viladated = datetime.now()
    ticket.save()
    TicketReason.objects.filter(ticket_id=ticket_id).delete()

    return redirect('evs:ViolationTickets')

def validated_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_reasons = data.get('reasons', [])
            remarks = data.get('remarks', '')

            ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket.ticket_status = 1
            ticket.remarks = remarks
            ticket.date_viladated = datetime.now()
            ticket.save()

            TicketReason.objects.filter(ticket_id=ticket_id).delete()

            for reason in selected_reasons:
                TicketReason.objects.create(
                    ticket_id = ticket_id,
                    reason_id = reason
                )

            return JsonResponse({'message': 'Violation updated successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('evs:ViolationTickets')

def update_id_status(request, ticket_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket.id_status = new_status
            ticket.save()

            return JsonResponse({'message': 'ID Status updated successfully'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('evs:ViolationTickets')