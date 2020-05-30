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

    wf2 = Workflow(name="TwoStep",
                   slug='twostep')
    wf2.save()
    ops = Operation.objects.get(name='script')
    el21 = Element(workflow=wf2,
                   operation=op,
                   op_params={'fred':'jim'},
                   slug_name="start",
                   is_initial=True)
    el21.save()
    el22 = Element(workflow=wf1,
                   operation=ops,
                   op_params={'fred':'jim'},
                   slug_name="script-one")
    el22.save()

    Link = apps.get_model('django_taskflow', 'Link')
    l212 = Link(source=el21,
                target=el22,
                slug_name="next")

    l212.save()

def remove_examples(apps, schema_editor):
    model_names = ['Workflow', 'Element', 'Link',]
    for model_name in model_names:
        model = apps.get_model('django_taskflow', model_name)
        for obj in model.objects.all():
            obj.delete()
