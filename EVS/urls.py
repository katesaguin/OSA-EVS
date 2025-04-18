from django.urls import path, include
from . import views

app_name = 'evs'

urlpatterns = [
    path('dashboard', views.dashboard_view, name="Dashboard"),
    path('tickets', views.violation_views, name="ViolationTickets"),
    path('student/tally', views.tally_views, name="Tally"),
    path('statistics', views.statistics_view, name="Statistics"),
    path('settings/academic-year', views.settings_academic, name="AcademicYear"),
    path('settings/user-management', views.settings_user_management, name="UserManagement"),
    path('ticket/<int:ticket_id>/details', views.ticketDetails_views, name="TicketDetails"),
    path('ticket/<int:ticket_id>/clear-ticket',views.clear_violation, name="ClearTicket"),
    path('ticket/<int:ticket_id>/validate', views.validated_ticket),
    path('ticket/<int:ticket_id>/update/id-status', views.update_id_status),
    path('ticket/<int:ticket_id>/update/violations', views.override_violation, name='ViolationUpdate'),
    path('student/<int:student_id>/save-status', views.save_status, name='Status'),
    path('student/<int:student_id>/details', views.tallyDetails_views, name='TallyDetails'),
    path('refresh-tickets', views.refresh_ticket_table, name='ViolationTable'),
    path('refresh-drashboard', views.refresh_dashboard_table, name='DashboardTable')
]