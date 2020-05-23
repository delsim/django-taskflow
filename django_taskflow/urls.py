from django.urls import path

from .app_name import app_name
from .views import WorkflowListView, WorkflowDetailView, element_view, TicketListView, TicketDetailView, TaskDetailView

urlpatterns = [
    path('workflows/', WorkflowListView.as_view(), name='workflows'),
    path('workflow/<slug>', WorkflowDetailView.as_view(), name="workflow"),
    path('element/<slug>/<slug_name>', element_view, name="element"),
    path('tickets/', TicketListView.as_view(), name="tickers"),
    path('ticket/<pk>', TicketDetailView.as_view(), name="ticker"),
    path('task/<pk>', TaskDetailView.as_view(), name="task"),
]
