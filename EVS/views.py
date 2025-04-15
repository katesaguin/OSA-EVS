from django.shortcuts import render, redirect
from .models import Student, Ticket, TicketReason, Reason, AcademicYear, StudentViolation
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
    tickets = tickets.order_by('-date_created')
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
    # Get search parameters
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    tickets = Ticket.objects.all()
    
    if student_name:
        name_terms = student_name.split()
        name_query = tickets
        for term in name_terms:
            name_query = name_query.filter(
                student__first_name__icontains=term) | \
                tickets.filter(student__middle_name__icontains=term) | \
                tickets.filter(student__last_name__icontains=term)
        tickets = name_query

    if student_id:
        tickets = tickets.filter(student__student_id__icontains=student_id)

    # Filter by exact date
    if filter_date:
        try:
            date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            tickets = tickets.filter(date_created__date=date_obj)
        except ValueError:
            pass  # Ignore invalid date format
    
    # Order results
    tickets = tickets.order_by('-date_created')
    
    # Paginate results
    page_obj = paginate_queryset(request, tickets, 15)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'system/tickets.html', context)

def tally_views(request):
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    
    students_with_tickets = Student.objects.filter(ticket__isnull=False).distinct()
    
    if student_name:
        name_terms = student_name.split()
        name_query = students_with_tickets
        
        for term in name_terms:
            name_query = name_query.filter(
                first_name__icontains=term) | \
                students_with_tickets.filter(middle_name__icontains=term) | \
                students_with_tickets.filter(last_name__icontains=term)
        
        students_with_tickets = name_query
    
    if student_id:
        students_with_tickets = students_with_tickets.filter(student_id__icontains=student_id)
    
    student_violations = []

    for student in students_with_tickets:
        id_violation = StudentViolation.objects.filter(student=student, violation_id=1)
        dress_code = StudentViolation.objects.filter(student=student, violation_id=2)
        uniform = StudentViolation.objects.filter(student=student, violation_id=3)
        id_not_claimed = StudentViolation.objects.filter(student=student, violation_id=4)
        
        # Collect all statuses
        statuses = []
        for qs in [id_violation, dress_code, uniform, id_not_claimed]:
            statuses += [violation.community_service_status for violation in qs]

        # Evaluate according to rules
        if 1 in statuses:
            community_service_status = 1
        elif 2 in statuses:
            community_service_status = 0
        elif not statuses:
            community_service_status = -1
        else:
            community_service_status = -1

        student_violations.append({
            'student': student,
            'id_violation_count': id_violation.count if id_violation else 0,
            'dress_code_count': dress_code.count if dress_code else 0,
            'uniform_count': uniform.count if uniform else 0,
            'id_not_claimed_count': id_not_claimed.count if id_not_claimed else 0,
            'community_service_status': community_service_status,
        })
    
    page_obj = paginate_queryset(request, student_violations, 15)
    
    context = {
        'student_violations': page_obj,
    }
    return render(request, 'system/tally.html', context)

def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def statistics_view(request):
    return render(request, 'system/statistics.html')

def settings_views(request):
    return render(request, 'system/settings.html')

@ensure_csrf_cookie
def ticketDetails_views(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    student = Student.objects.get(student_id=ticket.student.student_id)
    reasons = Reason.objects.all()
    ## ADD AUTO RETRIEVAL OF PHOTO 
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

            count_violation(ticket_id)

            TicketReason.objects.filter(ticket_id=ticket_id).delete()

            for reason in selected_reasons:
                TicketReason.objects.create(
                    ticket_id = ticket_id,
                    reason_id = reason
                )

            ## ADD AUTO EMAIL NOTIFICATION LOGIC

            return JsonResponse({'message': 'Violation updated successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('evs:ViolationTickets')

def update_id_status(request, ticket_id):
    if request.method == 'POST':
        try:
            content_type = request.META.get('CONTENT_TYPE', '')

            if 'application/json' in content_type:
                data = json.loads(request.body)
                new_status = data.get('status')
            else:
                new_status = request.POST.get('status')

            ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket.id_status = new_status
            ticket.save()

            if 'application/json' in content_type:
                return JsonResponse({'message': 'ID Status updated successfully'})
            else:
                return redirect('evs:ViolationTickets')
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('evs:ViolationTickets')

def count_violation(ticket_id):
    violations = Ticket.objects.get(ticket_id=ticket_id)
    student_id = violations.student_id

    def update_violation(violation_type):
        violation, _ = StudentViolation.objects.get_or_create(
            student_id=student_id,
            violation_id=violation_type,
            defaults={'count': 0}
        )
        violation.count += 1
        violation.save()
        letter_checker(student_id)
        cs_checker(student_id)

    if violations.id_violation:
        update_violation(1)

    if violations.dress_code_violation:
        update_violation(2)

    if violations.uniform_violation:
        update_violation(3)

    if violations.id_not_claimed_violation:
        update_violation(4)

def letter_checker(student_id):
    for_letter = StudentViolation.objects.filter(student_id=student_id)
    for violation in for_letter:
        if violation.count >= 2:
            violation.apology_letter = 1
            violation.apology_letter_status = 1
            violation.save()

def cs_checker(student_id):
    for_cs = StudentViolation.objects.filter(student_id=student_id)
    for violation in for_cs:
        if violation.count >= 3:
            violation.community_service = 1
            violation.community_service_status = 1
            violation.save()