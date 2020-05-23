from django.shortcuts import render

from django.views.generic import ListView, DetailView

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


def element_view(request, template_name="django_taskflow/element_detail.html", slug=None, slug_name=None):
    pass
