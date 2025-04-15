from django.shortcuts import render, redirect
from .models import Student, Ticket
from datetime import datetime
from django.core.paginator import Paginator
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
    # Get search parameters
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    
    # Start with all tickets
    tickets = Ticket.objects.all()
    
    # Apply filters if search parameters exist
    if student_name:
        # Split the search terms to allow searching for partial names
        name_terms = student_name.split()
        name_query = tickets
        
        for term in name_terms:
            # Filter by each term across all name fields (similar to SQL LIKE with wildcards)
            name_query = name_query.filter(
                student__first_name__icontains=term) | \
                tickets.filter(student__middle_name__icontains=term) | \
                tickets.filter(student__last_name__icontains=term)
        
        tickets = name_query
    
    if student_id:
        # Convert to string to handle both numeric and non-numeric IDs
        tickets = tickets.filter(student__student_id__icontains=student_id)
    
    # Order results
    tickets = tickets.order_by('-date_created')
    
    # Paginate results
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'system/tickets.html', context)

def tally_views(request):
    # Get search parameters
    student_name = request.GET.get('student_name', '')
    student_id = request.GET.get('student_id', '')
    
    # Start with all students who have tickets
    students_with_tickets = Student.objects.filter(ticket__isnull=False).distinct()
    
    # Apply filters for student name if provided
    if student_name:
        # Split the search terms to allow searching for partial names
        name_terms = student_name.split()
        name_query = students_with_tickets
        
        for term in name_terms:
            # Filter by each term across all name fields (similar to SQL LIKE with wildcards)
            name_query = name_query.filter(
                first_name__icontains=term) | \
                students_with_tickets.filter(middle_name__icontains=term) | \
                students_with_tickets.filter(last_name__icontains=term)
        
        students_with_tickets = name_query
    
    # Apply filter for student ID if provided
    if student_id:
        students_with_tickets = students_with_tickets.filter(student_id__icontains=student_id)
    
    # Create a list to store student violation summaries
    student_violations = []
    
    for student in students_with_tickets:
        # Count different violation types for this student
        id_violation_count = Ticket.objects.filter(student=student, id_violation=True).count()
        dress_code_count = Ticket.objects.filter(student=student, dress_code_violation=True).count()
        uniform_count = Ticket.objects.filter(student=student, uniform_violation=True).count()
        
        # Determine community service status
        # If total violations >= 5, community service is required
        total_violations = id_violation_count + id_not_claimed_count + dress_code_count + uniform_count
        
        # Check if there's a StudentViolation record for this student
        community_service_status = 'Not Required'
        if total_violations >= 5:
            try:
                student_violation = StudentViolation.objects.filter(student=student).first()
                if student_violation:
                    if student_violation.community_service_status == 0:
                        community_service_status = 'Awaiting'
                    elif student_violation.community_service_status == 1:
                        community_service_status = 'Completed'
                    else:
                        community_service_status = 'Awaiting'
                else:
                    community_service_status = 'Awaiting'
            except:
                community_service_status = 'Awaiting'
        
        # Add student data to the list
        student_violations.append({
            'student': student,
            'id_violation_count': id_violation_count,
            'dress_code_count': dress_code_count,
            'uniform_count': uniform_count,
            'community_service_status': community_service_status,
            'total_violations': total_violations
        })
    
    # Sort by total violations (descending)
    student_violations.sort(key=lambda x: x['total_violations'], reverse=True)
    
    # Paginate the results
    paginator = Paginator(student_violations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student_violations': page_obj,
    }
    return render(request, 'system/tally.html', context)

def statistics_view(request):
    return render(request, 'system/statistics.html')

def settings_views(request):
    return render(request, 'system/settings.html')

def ticketDetails_views(request):
    return render(request, 'system/ticket-details.html')