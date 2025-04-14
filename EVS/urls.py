from django.urls import path
from . import views

app_name = 'evs'

urlpatterns = [
    path('dashboard', views.dashboard_view, name="Dashboard"),
    path('tickets', views.violation_views, name="ViolationTickets"),
    path('tally', views.tally_views, name="Tally"),
    path('statistics', views.statistics_view, name="Statistics"),
    path('settings', views.settings_views, name="Settings"),
    path('ticket-details', views.ticketDetails_views, name="TicketDetails")
]