import pytest

from datetime import datetime

from django_taskflow.models import Workflow, Ticket, Task


@pytest.mark.django_db
def test_create_ticket(django_user_model):
    wf = Workflow.objects.get(slug='simple-steps')
    assert wf is not None

    user = django_user_model.objects.create(username="test user",
                                            password='tupass')
    context = {'user': user,
               }

    t = wf.create_ticket(context)
    assert t is not None
    assert isinstance(t, Ticket)

    tasks = Task.objects.filter(step__ticket=t)
    assert tasks.count() == 0

    task_1 = t.run_workflow(context)
    assert task_1 is not None

    t.last_check = datetime.now()
    t.last_checkor = context['user']

    tasks = Task.objects.filter(step__ticket=t).order_by('-creation')
    assert tasks.count() == 2

    task = tasks[0]
    assert task.status == task.Status.FINISHED

    task_2 = t.run_workflow_step(context)
    assert task_2 is None
