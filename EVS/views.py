from django.shortcuts import render, redirect
from .models import Student, Ticket, TicketReason, Reason, AcademicYear, StudentViolation, Semester, Violation
from datetime import datetime
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum
from django.template.loader import render_to_string
#import login_required

# GLOBAL FUNCTIONS
def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def count_violation(ticket_id, acad_year_id):
    violations = Ticket.objects.get(ticket_id=ticket_id)
    student_id = violations.student_id

    def update_violation(violation_type):
        violation = StudentViolation.objects.filter(
            student_id=student_id,
            violation_id=violation_type,
            acad_year_id=acad_year_id
        ).first()

        print(violation_type, student_id, acad_year_id)
        if violation:
            violation.count += 1
            violation.save()
        else:
            violation = StudentViolation.objects.create(
                student_id=student_id,
                violation_id=violation_type,
                acad_year_id=acad_year_id,
                count=1,
                community_service=0,
                community_service_status=0,
                apology_letter=0,
                apology_letter_status=0
            )

        letter_checker(student_id, acad_year_id)
        cs_checker(student_id, acad_year_id)

    if violations.id_violation:
        update_violation(1)

    if violations.dress_code_violation:
        update_violation(2)

    if violations.uniform_violation:
        update_violation(3)

    if violations.id_not_claimed_violation:
        update_violation(4)

def letter_checker(student_id, acad_year_id):
    for_letter = StudentViolation.objects.filter(student_id=student_id, acad_year_id=acad_year_id)
    for violation in for_letter:
        if violation.count >= 2:
            violation.apology_letter = 1
            violation.apology_letter_status = 1
            violation.save()

def cs_checker(student_id, acad_year_id):
    for_cs = StudentViolation.objects.filter(student_id=student_id, acad_year_id=acad_year_id)
    for violation in for_cs:
        if violation.count >= 3:
            violation.community_service = 1
            violation.community_service_status = 1
            violation.save()

def active_list():
    ay = AcademicYear.objects.filter(active=1)
    return ay




# GENERAL FUNCTIONS
def dashboard_view(request):
    current_month = datetime.now().month
    month_name = datetime(1900, current_month, 1).strftime('%B')

    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    tickets = Ticket.objects.filter(acad_year_id__in=ay_ids).order_by('-ticket_id')
    students = Student.objects.all()
    violations = StudentViolation.objects.filter(acad_year_id__in=ay_ids)\
        .values('violation_id')\
        .annotate(count=Sum('count'))
    id_violation = 0
    dresscode_violation = 0
    uniform_violation = 0
    

    for violation in violations:
        if violation['violation_id'] == 1 or violation['violation_id'] == 4:
            id_violation += violation['count']
        elif violation['violation_id'] == 2:
            dresscode_violation += violation['count']
        else:
            uniform_violation += violation['count']
    print(id_violation)
    return render(request, 'system/dashboard.html', {
        'id_violation': id_violation,
        'dresscode_violation': dresscode_violation,
        'uniform_violation': uniform_violation,
        'month': month_name,
        'tickets': tickets,
        'students': students,
    })

#@login_required (ALL FUNCTION)
def violation_views(request):
    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    # Get search parameters
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    # Filter tickets by active academic year(s)
    tickets = Ticket.objects.filter(acad_year_id__in=ay_ids)

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

    if filter_date:
        try:
            date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            tickets = tickets.filter(date_created__date=date_obj)
        except ValueError:
            pass

    tickets = tickets.order_by('-ticket_id')
    page_obj = paginate_queryset(request, tickets, 15)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'system/tickets.html', context)

def tally_views(request):
    # Get active academic year IDs
    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')

    # Filter only students with tickets under active academic years
    students_with_tickets = Student.objects.filter(
        ticket__acad_year_id__in=ay_ids
    ).distinct()

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
        id_violation = StudentViolation.objects.filter(student=student, violation_id=1, acad_year_id__in=ay_ids)
        dress_code = StudentViolation.objects.filter(student=student, violation_id=2, acad_year_id__in=ay_ids)
        uniform = StudentViolation.objects.filter(student=student, violation_id=3, acad_year_id__in=ay_ids)
        id_not_claimed = StudentViolation.objects.filter(student=student, violation_id=4, acad_year_id__in=ay_ids)

        statuses = []
        for qs in [id_violation, dress_code, uniform, id_not_claimed]:
            statuses += [violation.community_service_status for violation in qs]

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
            'id_violation_count': id_violation.aggregate(Sum('count'))['count__sum'] if id_violation else 0,
            'dress_code_count': dress_code.aggregate(Sum('count'))['count__sum'] if dress_code else 0,
            'uniform_count': uniform.aggregate(Sum('count'))['count__sum'] if uniform else 0,
            'id_not_claimed_count': id_not_claimed.aggregate(Sum('count'))['count__sum'] if id_not_claimed else 0,
            'community_service_status': community_service_status,
        })

    page_obj = paginate_queryset(request, student_violations, 15)

    context = {
        'student_violations': page_obj,
    }
    return render(request, 'system/tally.html', context)

def tallyDetails_views(request, student_id):
    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    tickets = Ticket.objects.filter(student_id=student_id, acad_year_id__in=ay_ids)
    student = Student.objects.get(student_id=student_id)
    violations = StudentViolation.objects.filter(student_id=student_id, acad_year_id__in=ay_ids)
    reasons = TicketReason.objects.all()
    all_reasons = Reason.objects.all()
    types = Violation.objects.all()
    return render(request, 'system/tally-details.html', {
        'student': student,
        'violations': violations,
        'types': types,
        'tickets': tickets,
        'reasons': reasons,
        'all_reasons': all_reasons
    })

@ensure_csrf_cookie
def ticketDetails_views(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    student = Student.objects.get(student_id=ticket.student.student_id)
    reasons = Reason.objects.all()
    violations = Violation.objects.all()

    ## ADD AUTO RETRIEVAL OF PHOTO 
    selected_reason_ids = TicketReason.objects.filter(ticket_id=ticket_id).values_list('reason_id', flat=True)
    return render(request, 'system/ticket-details.html', {
        'ticket': ticket,
        'student': student,
        'reasons': reasons,
        'selected': selected_reason_ids,
        'violations': violations
    })

def validated_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_reasons = data.get('reasons', [])
            remarks = data.get('remarks', '')

            ticket = Ticket.objects.get(ticket_id=ticket_id)

            count_violation(ticket_id, ticket.acad_year_id)

            TicketReason.objects.filter(ticket_id=ticket_id).delete()

            for reason in selected_reasons:
                TicketReason.objects.create(
                    ticket_id = ticket_id,
                    reason_id = reason
                )

            ticket.ticket_status = 1
            ticket.remarks = remarks
            ticket.date_viladated = datetime.now()
            ticket.save()
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

def save_status(request, student_id):
    if request.method == 'POST':
        # Print to check the request body
        print(request.body)
        
        # Parse incoming JSON data
        data = json.loads(request.body)  # Parse incoming JSON data
        violations = data.get('violations')
        
        print(violations)  # Check the data received
        
        ay_list = active_list()
        ay_ids = [ay.acad_year_id for ay in ay_list]

        for violation in violations:
            violation_id = violation.get('violation_id')
            letter_status = violation.get('letter_status')
            cs_render = violation.get('cs_render')
            cs_status = violation.get('cs_status')

            print(f"Updating violation {violation_id} with letter_status: {letter_status}, cs_render: {cs_render}, cs_status: {cs_status}")

            try:
                # Make sure the violation exists and belongs to the correct student and academic year
                student_violation = StudentViolation.objects.get(id=violation_id, student_id=student_id, acad_year_id__in=ay_ids)
                student_violation.apology_letter_status = letter_status
                student_violation.community_service = cs_render
                student_violation.community_service_status = cs_status
                student_violation.save()
                print(f"Successfully updated violation {violation_id}")
            except StudentViolation.DoesNotExist:
                print(f"Violation {violation_id} not found for student {student_id} in the current academic year.")
                return JsonResponse({'status': 'error', 'message': f"Violation {violation_id} not found for student {student_id}"}, status=400)

        return JsonResponse({'status': 'success', 'message': 'Data updated successfully'})

    




# REFRESH TABLES
def refresh_ticket_table(request):
    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    # Same filtering logic
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    tickets = Ticket.objects.filter(acad_year_id__in=ay_ids)

    if student_name:
        name_terms = student_name.split()
        for term in name_terms:
            tickets = tickets.filter(
                Q(student__first_name__icontains=term) |
                Q(student__middle_name__icontains=term) |
                Q(student__last_name__icontains=term)
            )

    if student_id:
        tickets = tickets.filter(student__student_id__icontains=student_id)

    if filter_date:
        try:
            date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            tickets = tickets.filter(date_created__date=date_obj)
        except ValueError:
            pass

    tickets = tickets.order_by('-ticket_id')
    page_obj = paginate_queryset(request, tickets, 15)

    html = render_to_string('system/partials/ticket-table-body.html', {'tickets': page_obj})
    return JsonResponse({'html': html})

def refresh_dashboard_table(request):
    ay_list = active_list()
    ay_ids = [ay.acad_year_id for ay in ay_list]

    # Same filtering logic
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    tickets = Ticket.objects.filter(acad_year_id__in=ay_ids)

    if student_name:
        name_terms = student_name.split()
        for term in name_terms:
            tickets = tickets.filter(
                Q(student__first_name__icontains=term) |
                Q(student__middle_name__icontains=term) |
                Q(student__last_name__icontains=term)
            )

    if student_id:
        tickets = tickets.filter(student__student_id__icontains=student_id)

    if filter_date:
        try:
            date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            tickets = tickets.filter(date_created__date=date_obj)
        except ValueError:
            pass

    tickets = tickets.order_by('-ticket_id')
    page_obj = paginate_queryset(request, tickets, 15)

    html = render_to_string('system/partials/dashboard-table-body.html', {'tickets': page_obj})
    return JsonResponse({'html': html})




# ADMIN ONLY
def override_violation(request, ticket_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        selected = data.get('violations', [])

        ticket = Ticket.objects.get(ticket_id=ticket_id)
        ticket.id_violation = 'id_violation' in selected
        ticket.dress_code_violation = 'dress_code_violation' in selected
        ticket.uniform_violation = 'uniform_violation' in selected

        violation_map = {
            1: ticket.id_violation,
            2: ticket.dress_code_violation,
            3: ticket.uniform_violation,
            4: ticket.id_not_claimed_violation
        }

        for violation_id, status in violation_map.items():
            violation = StudentViolation.objects.filter(
                student_id=ticket.student_id,
                acad_year_id=ticket.acad_year_id,
                violation_id=violation_id
            ).first()

            if violation:
                violation.count -= 1

                if violation.count < 2:
                    violation.apology_letter = 0
                    violation.apology_letter_status = 0

                if violation.count < 3:
                    violation.community_service = 0
                    violation.community_service_status = 0

                if violation.count <= 0:
                    violation.delete()
                else:
                    violation.save()

        ticket.ticket_status = 0
        ticket.date_validated = None  # if this is a DateTimeField
        ticket.id_status = 0
        ticket.remarks = ''
        ticket.save()

        TicketReason.objects.filter(ticket_id=ticket_id).delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def statistics_view(request):
    return render(request, 'system/statistics.html')

def clear_violation(request, ticket_id):
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    ticket.ticket_status = 2
    ticket.date_viladated = datetime.now()
    ticket.save()
    TicketReason.objects.filter(ticket_id=ticket_id).delete()

    return redirect('evs:ViolationTickets')




# SETTINGS BACKEND
def settings_user_management(request):
    return render(request, 'system/settings/user-management.html')

def settings_academic(request):
    if request.method == 'POST':
        desc = request.POST.get('ayLabel')
        sem = request.POST.get('aySem')
        start = request.POST.get('ayStart')
        end = request.POST.get('ayEnd')
        active = 'setActive' in request.POST

        if start > end:
            messages.warning(request, '!!  Year Start must be less than or equal to Year End  !!')
            return redirect('evs:AcademicYear')
        
        if AcademicYear.objects.filter(semester=sem, year_start=start, year_end=end).exists():
            messages.warning(request, '!!  Academic Year with this semester and date range already exists  !!')
            return redirect('evs:AcademicYear')

        AcademicYear.objects.create(
            description=desc,
            semester=sem,
            year_start=start,
            year_end=end,
            active=active,
            osa_id='111'
        )

        messages.success(request, 'Academic Year successfully created.')
        return redirect('evs:AcademicYear')
    if request.method == 'PATCH':
        data = json.loads(request.body)
        id = data.get('id')
        value = data.get('active') == '1'  # Ensures it's boolean

        ay = AcademicYear.objects.filter(acad_year_id=id).first()
        if ay:
            ay.active = value
            ay.save()
            return JsonResponse({
                'success': True,
                'description': ay.description
            })
        else:
            return JsonResponse({'success': False, 'error': 'Academic Year not found'}, status=404)

    ay_list = AcademicYear.objects.all().order_by('-acad_year_id')

    paginator = Paginator(ay_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    semesters = Semester.objects.all()
    return render(request, 'system/settings/academic-year.html', {
        'semesters': semesters,
        'ay': page_obj, 
        'activate_page': 'academic-year'
    })