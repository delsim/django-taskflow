"""Standard operations"""


from .models import Task


def enter_error_state(incoming_task, context, error_message):
    task = incoming_task.clone_task(context)
    task.status = task.Status.ERROR
    task.state = {'state': incoming_task.state,
                  'error': error_message}
    return task


def move_to_next(element, slug_name, incoming_task, context):
    targets = element.link_source.all()

    if len(targets) < 1:
        return None

    task = incoming_task.clone_task(context)
    for link in targets:
        if link.slug_name == slug_name:
            task.element = link.target
    return task


def init(incoming_task, element, context):
    """Basic initialisation of a first task."""

    if incoming_task.status == incoming_task.Status.COMPLETED:
        # move on to the next task; dont do on the first call in order to force a save
        task = move_to_next(element, "next", incoming_task, context)

        if task and task.element is None:
            return enter_error_state(incoming_task, context, "Initalisation task unable to move to next task")

        return task

    if incoming_task.status == incoming_task.Status.NEW:
        for k, v in element.op_params.items():
            incoming_task.state[k] = v

    incoming_task.status = incoming_task.Status.COMPLETED

    return incoming_task

def script(incoming_task, element, context):

    if incoming_task.status == incoming_task.Status.COMPLETED:
        # move on to the next task; dont do on the first call in order to force a save
        task = move_to_next(element, "next", incoming_task, context)

        if task and task.element is None:
            return enter_error_state(incoming_task, context, "Initalisation task unable to move to next task")

        return task

    op_params = element.op_params
    source_data = incoming_task.state

    print("Running script")
    print(op_params)
    print(source_data)

    incoming_task.status = incoming_task.Status.COMPLETED

    return incoming_task
