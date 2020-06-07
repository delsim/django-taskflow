from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from rest_framework.parsers import JSONParser

from .models import Workflow, Element, Ticket, Task


class WorkflowListView(ListView):
    model = Workflow


class WorkflowDetailView(DetailView):
    model = Workflow


class TicketDetailView(DetailView):
    model = Ticket


class TicketListView(ListView):
    model = Ticket


class TaskDetailView(DetailView):
    model = Task


class TaskListView(ListView):
    model = Task


class LiveTaskListView(TaskListView):
    queryset = Task.latest_tasks()


class AllTaskListView(TaskListView):
    queryset = Task.latest_tasks(False)


def element_view(request, template_name="django_taskflow/element_detail.html", slug=None, slug_name=None):
    pass


def update_ticket(request, template_name="django_taskflow/element_update.html", pk=None):
    pass


def start_ticket(request, slug=None):

    workflow = get_object_or_404(Workflow,
                                 slug=slug)

    context = Workflow.request_context(request)

    if request.method == 'GET':
        data = {}

    if request.method == 'POST':
        data = JSONParser().parse(request)

    t = workflow.create_ticket(context)

    return JsonResponse({'some': 'stuff',
                         'data': data,
                         'ticket': t.pk},
                        status=200)
