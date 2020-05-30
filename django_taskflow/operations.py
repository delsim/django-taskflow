"""Standard operations"""


from .models import Task


class OpBase:
    """Base classs for operations, providing methods through dispatch"""

    def __call__(self, incoming_task, element, context):
        print("OpBase call")
        print(incoming_task.status, incoming_task.status.__class__)

        try:
            label = incoming_task.status.label
        except:
            label = incoming_task.Status.labels[incoming_task.status]

        op_name = f"operate_{label}"
        op_func = getattr(self, op_name, None)
        # Missing method is a no-op
        if op_func is None:
            op_func = self.default_operation
        return op_func(incoming_task, element, context)

    def default_operation(self, incoming_task, element, context):
        return None

    @staticmethod
    def enter_error_state(incoming_task, context, error_message):
        task = incoming_task.clone_task(context)
        task.status = task.Status.ERROR
        task.state = {'state': incoming_task.state,
                      'error': error_message}
        return task


    @staticmethod
    def move_to_next(element, slug_name, incoming_task, context):
        targets = element.link_source.all()

        if len(targets) < 1:
            return None

        task = incoming_task.clone_task(context)
        for link in targets:
            if link.slug_name == slug_name:
                task.element = link.target
        return task


class Init(OpBase):

    def operate_Completed(self, incoming_task, element, context):
        task = self.move_to_next(element, "next", incoming_task, context)

        if task and task.element is None:
            return enter_error_state(incoming_task, context, "Initalisation task unable to move to next task")

        return task

    def operate_New(self, incoming_task, element, context):
        for k, v in element.op_params.items():
            incoming_task.state[k] = v

        incoming_task.status = incoming_task.Status.COMPLETED

        return incoming_task

    def default_operation(self, incoming_task, element, context):

        incoming_task.status = incoming_task.Status.COMPLETED

        return incoming_task


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
        task = OpBase.move_to_next(element, "next", incoming_task, context)

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

Script = script
