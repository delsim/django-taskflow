"""Creation and deletion of example data"""


def add_examples(apps, schema_editor):

    Workflow = apps.get_model('django_taskflow', 'Workflow')
    wf1 = Workflow(name="SimpleSteps",
                   slug='simple-steps')
    wf1.save()

    Element = apps.get_model('django_taskflow', 'Element')
    Operation = apps.get_model('django_taskflow', 'Operation')

    op = Operation.objects.get(name='__init')
    el11 = Element(workflow=wf1,
                   operation=op,#Operation.objects.get(name='__init'),
                   op_params={'fred':'jim'},
                   slug_name="start",
                   is_initial=True)
    el11.save()

    wf2 = Workflow(name="MultiStep",
                   slug='multistep')
    wf2.save()
    ops = Operation.objects.get(slug='script')
    el21 = Element(workflow=wf2,
                   operation=op,
                   op_params={'fred':'jim'},
                   slug_name="start",
                   is_initial=True)
    el21.save()
    el22 = Element(workflow=wf2,
                   operation=ops,
                   op_params={'fred':'jim',
                              'script_name': 'django_taskflow.example_data.sample_script'},
                   slug_name="script-one")
    el22.save()

    Link = apps.get_model('django_taskflow', 'Link')
    l212 = Link(source=el21,
                target=el22,
                slug_name="next")

    l212.save()

    et = Operation.objects.get(slug="external-task")
    el23 = Element(workflow=wf2,
                   operation=et,
                   op_params={'some_info':'el23'},
                   slug_name="et-one")
    el23.save()
    l223 = Link(source=el22,
                target=el23,
                slug_name="next")

    l223.save()

    wf3 = Workflow(name="SingleCall",
                   slug="single-call")
    wf3.save()
    el31 = Element(workflow=wf3,
                   operation=op,
                   op_params={},
                   slug_name="start",
                   is_initial=True)
    el31.save()
    el32 = Element(workflow=wf3,
                   operation=ops,
                   op_params={'script_name': 'django_taskflow.example_data.'},
                   slug_name="single_call")
    el32.save()
    l312 = Link(source=el31,
                target=el32,
                slug_name="next")
    l312.save()


def remove_examples(apps, schema_editor):
    model_names = ['OperatorTask', 'Task', 'Step', 'Workflow', 'Element', 'Link',]
    for model_name in model_names:
        model = apps.get_model('django_taskflow', model_name)
        for obj in model.objects.all():
            obj.delete()


def sample_script(*args, **kwargs):
    print("Sample script")
    rv = {'args': args,
          'kwargs': kwargs}
    return rv
