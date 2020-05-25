import pytest

from django.urls import reverse
from django_taskflow.models import Workflow


@pytest.mark.django_db
def test_get_workflows(client):

    resp = client.get(reverse('taskflow:workflows'))
    assert resp.status_code == 200

    wflow = Workflow.objects.all()[0]

    resp = client.get(reverse('taskflow:workflow', kwargs={'slug':wflow.slug}))
    assert resp.status_code == 200
