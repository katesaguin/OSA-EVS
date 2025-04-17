from django.urls import path, include
from . import views

app_name = 'evs'

urlpatterns = [
    path('dashboard', views.dashboard_view, name="Dashboard"),
    path('tickets', views.violation_views, name="ViolationTickets"),
    path('tally', views.tally_views, name="Tally"),
    path('statistics', views.statistics_view, name="Statistics"),
    path('settings', views.settings_views, name="Settings"),
    path('settings/profile', views.settingsProfile_view, name="SettingsProfile"),
    path('settings/academic-year', views.settingsAcademicYear_view, name="SettingsAcademicYear"),
    path('settings/user-management', views.settingsUserManagement_view, name="SettingsUserManagement"),
    path('<int:ticket_id>/details', views.ticketDetails_views, name="TicketDetails"),
    path('<int:ticket_id>/clear-ticket',views.clear_violation, name="ClearTicket"),
    path('<int:ticket_id>/validate', views.validated_ticket),
    path('<int:ticket_id>/update/id-status', views.update_id_status),
]

