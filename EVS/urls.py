from django.urls import path, include
from . import views

app_name = 'evs'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('dashboard', views.dashboard_view, name="Dashboard"),
    path('tickets', views.violation_views, name="ViolationTickets"),
    path('student/tally', views.tally_views, name="Tally"),
    path('statistics', views.statistics_view, name="Statistics"),
    path('settings/academic-year', views.settings_academic, name="AcademicYear"),
    path('settings/user-management', views.settings_user_management, name="UserManagement"),
    path('settings/my-profile', views.settings_my_profile, name="MyProfile"),
    path('settings/ticket-settings', views.settings_ticket_settings, name="TicketSettings"),
    path('ticket/<int:ticket_id>/details', views.ticketDetails_views, name="TicketDetails"),
    path('ticket/<int:ticket_id>/clear-ticket',views.clear_violation, name="ClearTicket"),
    path('ticket/<int:ticket_id>/validate', views.validated_ticket),
    path('ticket/<int:ticket_id>/update/id-status', views.update_id_status),
    path('ticket/<int:ticket_id>/update/violations', views.override_violation, name='ViolationUpdate'),
    path('student/<int:student_id>/save-status', views.save_status, name='Status'),
    path('student/<int:student_id>/details', views.tallyDetails_views, name='TallyDetails'),
    path('refresh-tickets', views.refresh_ticket_table, name='ViolationTable'),
    path('refresh-drashboard', views.refresh_dashboard_table, name='DashboardTable'),
    path('refresh-tally', views.refresh_tally_table, name='TallyTable'),
    path('get-reasons', views.get_reasons, name='StatisticReasons'),
    path('delete-academic-year/<int:acad_year_id>', views.delete_academic_year),
]

