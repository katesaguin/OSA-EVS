from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('ticket-submission', views.submit_ticket, name="TicketSubmit"),
    path('<int:acad_year_id>/get-academic-year', views.get_academic, name="getAcademicYear"),
    path('<int:ticket_id>/check_ticket', views.ticket_checker),
    path('<int:ticket_id>/get-data', views.get_ticket_data),
    path('<int:ticket_id>/update-status', views.id_status_update)
]
