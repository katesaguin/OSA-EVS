from django.http import JsonResponse
from EVS.models import *
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def submit_ticket(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            ticket_data = data.get("ticket")
            student_data = data.get("student")

            student_obj, created = Student.objects.get_or_create(
                student_id=student_data.get("student_id"),
                defaults={
                    "first_name": student_data.get("first_name"),
                    "last_name": student_data.get("last_name"),
                    "middle_name": student_data.get("middle_name"),
                }
            )

            acad_year_obj = AcademicYear.objects.get(pk=ticket_data.get("acad_year"))
            semester_obj = Semester.objects.get(pk=ticket_data.get("semester"))
            student_obj = Student.objects.get(pk=ticket_data.get("student_id"))

            Ticket.objects.create(
                ticket_id=ticket_data.get("ticket_id"),
                uniform_violation=ticket_data.get("uniform_violation"),
                dress_code_violation=ticket_data.get("dress_code_violation"),
                id_violation=ticket_data.get("id_violation"),
                id_not_claimed_violation=ticket_data.get("id_not_claimed_violation"),
                submitted_by=str(ticket_data.get("ssio_id")),  # Replace with staff name 
                id_status=ticket_data.get("id_status"),
                ticket_status=ticket_data.get("ticket_status"),
                remarks=ticket_data.get("remarks"),
                photo_path=ticket_data.get("photo_path"),
                date_created=ticket_data.get('date_created'),
                date_validated=ticket_data.get('date_validated'),
                acad_year=acad_year_obj, 
                semester=semester_obj,
                student=student_obj,
                override_status=0,
                osa_id = 0
            )

            return JsonResponse({"message": "Ticket submitted and saved", "success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
def get_academic(request, acad_year_id):
    latest_acad_year = AcademicYear.objects.get(pk=acad_year_id)
    if latest_acad_year:
        data = {
            'acad_year_id': latest_acad_year.acad_year_id,
            'description': latest_acad_year.description,
            'year_start': latest_acad_year.year_start,
            'year_end': latest_acad_year.year_end,
            'semester': latest_acad_year.semester,
            'active': latest_acad_year.active
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No academic years found'}, status=404)
    
def ticket_checker(request, ticket_id):
    if request.method == "GET":
        try:
            ticket = Ticket.objects.filter(ticket_id=ticket_id).exists()

            if ticket:
                return JsonResponse({'message': 'Already Exists', 'success': False})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
       
def get_ticket_data(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        data = {
            'id_status': ticket.id_status,
            'ticket_status': ticket.ticket_status,
            'id_violation': ticket.id_violation,
            'uniform_violation': ticket.uniform_violation,
            'dress_code_violation': ticket.dress_code_violation,
            'id_not_claimed_violation': ticket.id_not_claimed_violation
        }
        return JsonResponse(data)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'No Ticket found'}, status=404)

@csrf_exempt
def id_status_update(request, ticket_id):
    try:
        data = json.loads(request.body)
        id_status = data.get('id_status')
        ticket = Ticket.objects.get(pk=ticket_id)
        
        ticket.id_status = id_status
        ticket.save()
        
        return JsonResponse({'success': True, 'message': 'Ticket id status updated successfully'})
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'No Ticket found'}, status=404)