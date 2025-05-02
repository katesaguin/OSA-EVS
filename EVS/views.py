from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from datetime import datetime
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db.models import Sum, Q, Count
from django.template.loader import render_to_string
#import login_required

# GLOBAL FUNCTIONS
def paginate_queryset(request, queryset, per_page):
    page_number = request.GET.get('page')
    paginator = Paginator(queryset, per_page)
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

        violation_checker(student_id, acad_year_id)

    if violations.uniform_violation:
        update_violation(1)

    if violations.dress_code_violation:
        update_violation(2)

    if violations.id_violation:
        update_violation(3)

    if violations.id_not_claimed_violation:
        update_violation(4)

def violation_checker(student_id, acad_year_id):
    for_letter = StudentViolation.objects.filter(student_id=student_id, acad_year_id=acad_year_id)
    for violation in for_letter:
        if violation.count >= 2:
            if violation.apology_letter_status != 2:
                violation.apology_letter = 1
                violation.apology_letter_status = 1
        else:
            violation.apology_letter = 0
            violation.apology_letter_status = 0 

        if violation.count >= 3:
            if violation.community_service == 0:
                violation.community_service = 3
                violation.community_service_status = 1
        else:
            violation.community_service = 0
            violation.community_service_status = 0
        
        violation.save()

def active_list():
    ay = AcademicYear.objects.filter(active=1)
    return ay

def readjust_violations(ticket):
    violation_map = {
        1: ticket.uniform_violation,
        2: ticket.dress_code_violation,
        3: ticket.id_violation,
        4: ticket.id_not_claimed_violation
    }

    for violation_id in violation_map.items():
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

def get_reasons(request):
    from_date = request.GET.get('from_date')
    to_date   = request.GET.get('to_date')
    ay_filter = request.GET.get('academic_list')

    qs = Ticket.objects.filter(ticket_status=1)
    ay = None

    try:
        if ay_filter:
            ay = AcademicYear.objects.get(pk=ay_filter)
        else:
            ay = AcademicYear.objects.get(active=1)
        qs = qs.filter(acad_year_id=ay.acad_year_id)
    except AcademicYear.DoesNotExist:
        ay = None

    if from_date and to_date:
        try:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            end = datetime.strptime(to_date, '%Y-%m-%d')
            qs = qs.filter(date_validated__date__range=(start, end))
        except ValueError:
            pass


    ticket_ids = qs.values_list('ticket_id', flat=True)
    reason_counts = (
        TicketReason.objects
        .filter(ticket_id__in=ticket_ids)
        .values('reason_id')
        .annotate(count=Count('reason_id'))
        .order_by('-count')
    )

    results = []
    for entry in reason_counts:
        try:
            r = Reason.objects.get(reason_id=entry['reason_id'])
            results.append({
                'reason_id':   entry['reason_id'],
                'reason_text': r.description,
                'count':       entry['count'],
                'color':       r.color,
            })
        except Reason.DoesNotExist:
            continue

    return JsonResponse({'reason_counts': results})




# GENERAL FUNCTIONS
def dashboard_view(request):
    current_month = datetime.now().month
    month_name = datetime(1900, current_month, 1).strftime('%B')

    ay_id = active_list()

    tickets = Ticket.objects.filter(acad_year_id__in=ay_id).order_by('-ticket_id')
    students = Student.objects.all()
    violations = StudentViolation.objects.filter(acad_year_id__in=ay_id)\
        .values('violation_id')\
        .annotate(count=Sum('count'))
    id_violation = 0
    dresscode_violation = 0
    uniform_violation = 0
    id_not_claimed_violation = 0
    

    for violation in violations:
        if violation['violation_id'] == 3:
            id_violation += violation['count']
        elif violation['violation_id'] == 2:
            dresscode_violation += violation['count']
        elif violation['violation_id'] == 4:
            id_not_claimed_violation += violation['count']
        else:
            uniform_violation += violation['count']

    return render(request, 'system/dashboard.html', {
        'id_violation': id_violation,
        'dresscode_violation': dresscode_violation,
        'uniform_violation': uniform_violation,
        'id_not_claimed': id_not_claimed_violation,
        'month': month_name,
        'tickets': tickets,
        'students': students,
    })

#@login_required (ALL FUNCTION)
def violation_views(request):
    ay_id = active_list()

    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    tickets = Ticket.objects.filter(acad_year_id__in=ay_id)

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
    page_obj = paginate_queryset(request, tickets, 10)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'system/tickets.html', context)

def tally_views(request):
    ay_id = active_list()

    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')

    students_with_tickets = Student.objects.filter(
        ticket__acad_year_id__in=ay_id, ticket__ticket_status = 1
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
        
        uniform = StudentViolation.objects.filter(student=student, violation_id=1, acad_year_id__in=ay_id)
        dress_code = StudentViolation.objects.filter(student=student, violation_id=2, acad_year_id__in=ay_id)
        id_violation = StudentViolation.objects.filter(student=student, violation_id=3, acad_year_id__in=ay_id)
        id_not_claimed = StudentViolation.objects.filter(student=student, violation_id=4, acad_year_id__in=ay_id)

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
    ay_id = active_list()

    tickets = Ticket.objects.filter(student_id=student_id, acad_year_id__in=ay_id, ticket_status=1 or 2)
    student = Student.objects.get(student_id=student_id)
    violations = StudentViolation.objects.filter(student_id=student_id, acad_year_id__in=ay_id)
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

#@ensure_csrf_cookie
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
            now = datetime.now()
            ay_id = AcademicYear.objects.get(active=1)

            ticket = Ticket.objects.get(ticket_id=ticket_id)
            TicketReason.objects.filter(ticket_id=ticket_id).delete()

            for reason in selected_reasons:
                TicketReason.objects.create(
                    ticket_id = ticket_id,
                    reason_id = reason,
                    acad_year_id = ay_id.acad_year_id,
                    date_created = now
                )

            if ticket.ticket_status != 1:
                count_violation(ticket_id, ticket.acad_year_id)

                ticket.ticket_status = 1
                ticket.remarks = remarks
                ticket.date_validated = now
                ticket.save()
                ## ADD AUTO EMAIL NOTIFICATION LOGIC

                return JsonResponse({'message': 'Violation updated successfully'})
            else:
                return JsonResponse({'message': 'Violation is already resolved'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('evs:ViolationTickets')

def update_id_status(request, ticket_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            new_status = data.get('status')

            ticket = Ticket.objects.get(pk=ticket_id)
            ticket.id_status = new_status
            ticket.save()

            return JsonResponse({'message': 'ID Status updated successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def save_status(request, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        violations = data.get('violations')
        
        ay_id = active_list()

        for violation in violations:
            violation_id = violation.get('violation_id')
            letter_status = violation.get('letter_status')
            cs_render = violation.get('cs_render')
            cs_status = violation.get('cs_status')

            try:
                student_violation = StudentViolation.objects.get(id=violation_id, student_id=student_id, acad_year_id__in=ay_id)
                
                if letter_status is not None:
                    student_violation.apology_letter_status = letter_status
                
                if cs_render is not None:
                    student_violation.community_service = cs_render
                
                if cs_status is not None:
                    student_violation.community_service_status = cs_status
                
                student_violation.save()
            except StudentViolation.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f"Violation {violation_id} not found for student {student_id}"}, status=400)

        return JsonResponse({'status': 'success', 'message': 'Data updated successfully'})

    




# REFRESH TABLES
def refresh_ticket_table(request):
    ay_id = active_list()

    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    filter_date = request.GET.get('filter_date', '')

    tickets = Ticket.objects.filter(acad_year_id__in=ay_id)

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
    page_obj = paginate_queryset(request, tickets, 10)

    html = render_to_string('system/partials/ticket-table-body.html', {'tickets': page_obj})
    return JsonResponse({'html': html})

def refresh_dashboard_table(request):
    ay_id = active_list()

    tickets = Ticket.objects.filter(acad_year_id__in=ay_id)
    students = Student.objects.all()
    tickets = tickets.order_by('-ticket_id')
    page_obj = paginate_queryset(request, tickets, 5)

    html = render_to_string('system/partials/dashboard-table-body.html', {
        'tickets': page_obj,
        'students': students
        })
    return JsonResponse({'html': html})

def refresh_tally_table(request):
    ay_id = active_list()

    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')

    students_with_tickets = Student.objects.filter(
        ticket__acad_year_id__in=ay_id, ticket__ticket_status = 1
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
        uniform = StudentViolation.objects.filter(student=student, violation_id=1, acad_year_id__in=ay_id)
        dress_code = StudentViolation.objects.filter(student=student, violation_id=2, acad_year_id__in=ay_id)
        id_violation = StudentViolation.objects.filter(student=student, violation_id=3, acad_year_id__in=ay_id)
        id_not_claimed = StudentViolation.objects.filter(student=student, violation_id=4, acad_year_id__in=ay_id)

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
    html = render_to_string('system/partials/tally-table-body.html', {'tickets': page_obj})
    return JsonResponse({'html': html})



# ADMIN ONLY
def override_violation(request, ticket_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected = data.get('violations', [])

        ticket = Ticket.objects.get(ticket_id=ticket_id)
        ticket.id_violation = 'id_violation' in selected
        ticket.dress_code_violation = 'dress_code_violation' in selected
        ticket.uniform_violation = 'uniform_violation' in selected
        if ticket.ticket_status == 1:
            readjust_violations(ticket)

        violation_checker(ticket.student_id, ticket.acad_year_id)

        ticket.ticket_status = 0
        ticket.date_validated = None 
        ticket.id_status = 0
        ticket.remarks = ''
        ticket.save()

        TicketReason.objects.filter(ticket_id=ticket_id).delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def statistics_view(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    ay_filter = request.GET.get('academic_list')
    
    qs = Ticket.objects.filter(ticket_status=1)
    ay = None

    try:
        if ay_filter:
            ay = AcademicYear.objects.get(pk=ay_filter)
        else:
            ay = AcademicYear.objects.get(active=1)
        qs = qs.filter(acad_year_id=ay.acad_year_id)
    except AcademicYear.DoesNotExist:
        ay = None

    if from_date and to_date:
        try:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            end = datetime.strptime(to_date, '%Y-%m-%d')
            qs = qs.filter(date_validated__date__range=(start, end))
        except ValueError:
            pass

    total_tickets = qs.count()

    id_violation = qs.filter(id_violation=True).count()
    uniform_violation = qs.filter(uniform_violation=True).count()
    dress_code_violation = qs.filter(dress_code_violation=True).count()
    id_not_claimed_violation = qs.filter(id_not_claimed_violation=True).count()
    total_violations = id_violation + uniform_violation + dress_code_violation + id_not_claimed_violation

    ticket_ids = qs.values_list('ticket_id', flat=True)
    reason_ids = TicketReason.objects.filter(ticket_id__in=ticket_ids).values_list('reason_id', flat=True)
    reasons = Reason.objects.filter(reason_id__in=reason_ids)

    semesters = Semester.objects.all()
    ay_list = AcademicYear.objects.all()

    return render(request, 'system/statistics.html', {
        'from_date': from_date,
        'to_date': to_date,
        'selected_ay': ay.acad_year_id if ay else None,

        'id_violation': id_violation,
        'uniform_violation': uniform_violation,
        'dress_code_violation': dress_code_violation,
        'id_not_claimed_violation': id_not_claimed_violation,
        'total_violations': total_violations,

        'ay': ay.description if ay else 'N/A',
        'semester': Semester.objects.get(pk=ay.semester).semester if ay else 'N/A',

        'reasons': reasons,
        'ay_list': ay_list,
        'semesters': semesters,

        'total_tickets': total_tickets,
    })

def clear_violation(request, ticket_id):
    if request.method == 'POST':
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        data = json.loads(request.body)
        remarks = data.get('remarks')

        if ticket.ticket_status != 0:
            readjust_violations(ticket)

        violation_checker(ticket.student_id, ticket.acad_year_id)

        ticket.ticket_status = 2
        ticket.remarks = remarks
        ticket.id_status = 0
        ticket.date_viladated = datetime.now()
        ticket.save()

        TicketReason.objects.filter(ticket_id=ticket_id).delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



# SETTINGS BACKEND
def settings_user_management(request):
    return render(request, 'system/settings/user-management.html')

def settings_academic(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acad_data = data.get('acad_year', {})

            desc = acad_data.get('description')
            sem = int(acad_data.get('semester'))
            start = acad_data.get('year_start')
            end = acad_data.get('year_end')
            active = bool(int(acad_data.get('active', 0)))

            if start > end:
                return JsonResponse({'success': False, 'error': 'Year Start must be less than or equal to Year End'}, status=400)
            
            if AcademicYear.objects.filter(semester=sem, year_start=start, year_end=end).exists():
                return JsonResponse({'success': False, 'error': 'Academic Year with this semester and date range already exists'}, status=400)

            if active:
                AcademicYear.objects.update(active=False)

            new_ay = AcademicYear.objects.create(
                description=desc,
                semester=sem,
                year_start=start,
                year_end=end,
                active=active,
                osa_id=111
            )
            
            return JsonResponse({'success': True, 'message': 'Academic year added successfully', 'acad_year_id': new_ay.acad_year_id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    if request.method == 'PATCH':
        data = json.loads(request.body)
        id = data.get('id')
        value = data.get('active') == '1'

        ay = AcademicYear.objects.filter(acad_year_id=id).first()
        if ay:
            if value:
                AcademicYear.objects.update(active=False)

            ay.active = value
            ay.save()
            return JsonResponse({
                'success': True,
                'description': ay.description
            })
        else:
            return JsonResponse({'success': False, 'error': 'Academic Year not found'}, status=404)

    ay_list = AcademicYear.objects.all().order_by('-acad_year_id')

    page_obj = paginate_queryset(request, ay_list, 3)
    semesters = Semester.objects.all()
    return render(request, 'system/settings/academic-year.html', {
        'semesters': semesters,
        'ay': page_obj, 
        'activate_page': 'academic-year'
    })

def delete_academic_year(request, acad_year_id):
    if request.method == 'DELETE':
        try:
            tickets = Ticket.objects.filter(acad_year_id=acad_year_id).count()
            if tickets == 0:
                ay = AcademicYear.objects.get(acad_year_id=acad_year_id)
                ay.delete()
                return JsonResponse({'message': 'Academic year deleted successfully.'})
            else:
                return JsonResponse({'message': 'Existing tickets under this Academic Year exists'})
        except AcademicYear.DoesNotExist:
            return JsonResponse({'message': 'Academic year not found.'}, status=404)
    return HttpResponseNotAllowed(['DELETE'])