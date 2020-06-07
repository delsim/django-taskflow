"""Standard operations"""


from .models import Task, Operation


class OpBase:
    """Base classs for operations, providing methods through dispatch"""

    def __call__(self, incoming_task, element, context):
        print("OpBase call")
        print(incoming_task)
        print(element)
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
        print(f"In default op for {incoming_task} on {element}")
        return None

    def operate_Error(self, incoming_task, element, context):
        return None

    def operate_Completed(self, incoming_task, element, context):
        """Move to next element"""
        task = self.move_to_next(element, "next", incoming_task, context)

        if task and task.element is None:
            return self.enter_error_state(incoming_task, context, "Default operation on task unable to move to next task")

        return task

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

    def operate_New(self, incoming_task, element, context):
        for k, v in element.op_params.items():
            incoming_task.state[k] = v

        incoming_task.status = incoming_task.Status.COMPLETED

        return incoming_task

    def default_operation(self, incoming_task, element, context):

        incoming_task.status = incoming_task.Status.COMPLETED

        return incoming_task


class Script(OpBase):

    def default_operation(self, incoming_task, element, context):

        op_params = element.op_params

        try:
            func = Operation.load_object_by_name(op_params['script_name'])
        except:
            print("Cannot locate script_name in ", op_params)

        res = func(element_parameters = op_params,
                   source_data = incoming_task.state)

        task = incoming_task.clone_task(context)
        task.state = res
        task.status = task.Status.COMPLETED

        return task


class ExternalTask(OpBase):
    """An external task, that pauses progress until resolved."""

    def default_operation(self, incoming_task, element, context):
        print("External default")
        return None

    def operate_New(self, incoming_task, element, context):
        print("External new")
        # Move new task into waiting state, set up other db entries as needed
        pass

    def operate_Waiting(self, incoming_task, element, context):
        print("External waiting")
        # Do nothing; moving to updated will happen once the external task is processed
        return None

    def operate_Updated(self, incoming_task, element, context):
        print("External updated")
        # Task might have external update; if so process and return a completed task
        pass

    def operate_Error(self, incoming_task, element, context):
        self.cleanup_task(incoming_task, element, context)
        # unless error is handled elsewhere, return None to move to final state
        return None

    def operate_Completed(self, incoming_task, element, context):
        print("External completed")
        # Clean up additional db entries and move to next state")
        self.cleanup_task(incoming_task, element, context)

    def cleanup_task(self, incoming_task, element, context):
        pass
