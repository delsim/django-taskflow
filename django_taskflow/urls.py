from django.urls import path
from django.contrib.auth.decorators import login_required

from .app_name import app_name

from .views import WorkflowListView, WorkflowDetailView, element_view, TicketListView, TicketDetailView, TaskDetailView
from .views import TaskListView, LiveTaskListView, AllTaskListView

from .views import update_ticket, start_ticket

urlpatterns = [
    path('workflows/', WorkflowListView.as_view(), name='workflows'),
    path('workflow/detail/<slug>', WorkflowDetailView.as_view(), name="workflow"),
    path('workflow/start/<slug>', login_required(start_ticket), name="initiate_workflow"),

    path('element/<slug>/<slug_name>', element_view, name="element"),

    path('tickets/', TicketListView.as_view(), name="tickets"),
    path('ticket/detail/<pk>', TicketDetailView.as_view(), name="ticket"),
    path('ticket/update/<pk>', update_ticket, name="ticket-update"),

    path('task/<pk>', TaskDetailView.as_view(), name="task"),
    path('full_task_list/', TaskListView.as_view(), name="full_task_list"),
    path('all_tasks/', AllTaskListView.as_view(), name="all_tasks"),
    path('live_tasks/', LiveTaskListView.as_view(), name="live_tasks"),
]
