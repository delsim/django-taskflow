import pytest

from django_taskflow.models import Workflow, Ticket


@pytest.mark.django_db
def test_create_ticket(django_user_model):
    wf = Workflow.objects.all()[0]
    assert wf is not None

    user = django_user_model.objects.create(username="test user",
                                            password='tupass')
    context = {'user': user,
               }

    t = wf.create_ticket(context)
    assert t is not None
    assert isinstance(t, Ticket)
