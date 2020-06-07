import pytest

from django.urls import reverse
from django_taskflow.models import Workflow, Ticket


@pytest.mark.django_db
def test_get_workflows(client):

    resp = client.get(reverse('taskflow:workflows'))
    assert resp.status_code == 200

    wflow = Workflow.objects.all()[0]

    resp = client.get(reverse('taskflow:workflow', kwargs={'slug':wflow.slug}))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_start_workflow(client, django_user_model):

    this_user = django_user_model.objects.create(username="fred")
    this_user.set_password("jim")
    this_user.save()

    client.login(username="fred",
                 password="jim")

    wflow = Workflow.objects.all()[0]
    num_tickets = Ticket.objects.filter(workflow=wflow).count()

    resp = client.get(reverse('taskflow:initiate_workflow', kwargs={'slug':wflow.slug}))
    assert resp.status_code == 200
    assert Ticket.objects.filter(workflow=wflow).count() == num_tickets + 1
