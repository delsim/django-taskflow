import pytest


from django_taskflow.models import Operation, Task


def some_function(x, y):
    return x + y


def test_operation():
    op = Operation(name="name",
                   slug="slug",
                   description="desc",
                   function="django_taskflow.tests.test_operation.some_function")

    f = op.function_as_callable()
    assert f is not None
    assert f == some_function

    assert f(1, 2) == 3


def test_task_types():
    t = Task()
    print(t.status.__class__)
    print(t.status.label)
    for p in Task.Status.labels:
        print(p)
