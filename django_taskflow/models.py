import importlib

import datetime

from django.db import models
from django.db.models import Q, F, OuterRef, Max, Subquery

from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib.postgres.fields import JSONField

from .app_name import app_name

User = settings.AUTH_USER_MODEL

class NameSlugBase(models.Model):
    name = models.CharField(max_length=100, unique=False, blank=False, null=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=False)

    def save(self, *args, **kwargs):
        if self.slug is None:
            pslug = slugify(self.slug)
            psc = self.__class__.objects.filter(slug__startswith=pslug).count()
            if psc > 0:
                self.slug = f"{pslug}{psc}"
            else:
                self.slug = psc
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Operation(NameSlugBase):
    function = models.CharField(max_length=100, unique=False, blank=False, null=False)
    description = models.TextField()

    @staticmethod
    def load_object_by_name(name):
        name_parts = name.split('.')
        mod_name = ".".join(name_parts[:-1])
        module = importlib.import_module(mod_name)
        return getattr(module, name_parts[-1])

    def function_as_callable(self):
        """Get the task processing function for this operation"""

        func = Operation.load_object_by_name(self.function)
        try:
            # If a class, then instantiate it
            func = func()
        except:
            pass
        return func


class OperationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'function']


class Workflow(NameSlugBase):
    description = models.TextField()

    def get_absolute_url(self):
        return reverse(f"{app_name}:workflow", kwargs={'slug': self.slug})

    def get_new_ticket_url(self):
        return reverse(f"{app_name}:initiate_workflow", kwargs={'slug': self.slug})

    @staticmethod
    def user_context(user):
        """Form a context from just user info"""
        context = {'user': user,
                   }
        return context

    @staticmethod
    def request_context(request):
        """Form a context from the curent request."""
        context = {'user': request.user,
                   }
        return context

    def create_ticket(self, context):
        t = Ticket(workflow=self,
                   creator=context['user'])
        t.save()

        if 'initial_arguments' in context:
            # Perform init step on the ticket
            t.run_workflow_step(context)
        return t


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]

    def create_ticket(self, request, queryset):
        for q in queryset.all():
            context = Workflow.request_context(request)
            ticket = q.create_ticket(context)
            ticket.run_workflow_step(context)

    create_ticket.short_description = "Create a new ticket"

    actions = [create_ticket, ]


class Element(models.Model):
    workflow = models.ForeignKey(Workflow, blank=False, unique=False, null=False, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, blank=False, unique=False, null=False, on_delete=models.CASCADE)
    op_params = JSONField(null=False, blank=False, unique=False)
    slug_name = models.SlugField(max_length=100, unique=False)
    is_initial = models.BooleanField(default=False, unique=False, null=False)

    def __str__(self):
        return f"{self.workflow}:{self.slug_name}"

    class Meta:
        constraints = [models.UniqueConstraint(fields=['workflow', 'slug_name'], name="uniqueness_workflow_slug"),
                       models.UniqueConstraint(fields=['workflow'], condition=Q(is_initial=True), name="unique_initial_element"),
                       ]

    def process_task(self, task, context):
        """Run a single step on the task using this element.

        If there is a state change, then return the new task. Otherwise return None.
        The new task could be a completed version of the argument, or a new task to be
        processed by another element.

        A task can always be passed for processing by its element. The processing function is
        responsible for moving the task on to another element; nothing else will change the
        current element of a ticket.
        """
        if task.status == task.Status.FINISHED or task.status== task.Status.TERMINATED:
            return None

        func = self.operation.function_as_callable()
        try:
            new_task = func(incoming_task=task,
                            element=self,
                            context=context)
        except Exception as e:
            new_task = task.clone_task(context)
            new_task.status = task.Status.ERROR
            new_task.state = {'state': task.state,
                              'error': str(e)}

        if new_task is None:
            if task.status == task.Status.COMPLETED or task.status== task.Status.ERROR:
                new_task = task.clone_task(context)
                if task.status == task.Status.COMPLETED:
                    new_task.status = task.Status.FINISHED
                else:
                    new_task.status = task.Status.TERMINATED

        return new_task


class ElementAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'operation', 'slug_name', 'is_initial',]
    list_filter = ['is_initial', 'operation', 'workflow',]


class Link(models.Model):
    source = models.ForeignKey(Element, blank=False, unique=False, null=False, on_delete=models.CASCADE, related_name="link_source")
    target = models.ForeignKey(Element, blank=False, unique=False, null=False, on_delete=models.CASCADE, related_name="link_target")
    slug_name = models.SlugField(max_length=100, unique=False)

    def save(self, *args, **kwargs):
        if self.source.workflow != target.source.workflow:
            raise ValueError("Cannor have a link berween elements of different workflows")
        return super().save(*args, **kwargs)


class LinkAdmin(admin.ModelAdmin):
    list_display = ['source', 'target', 'slug_name', ]
    list_filter = ['slug_name', ]


class Ticket(models.Model):
    workflow = models.ForeignKey(Workflow, blank=False, unique=False, null=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, blank=False, unique=False, null=False, on_delete=models.CASCADE)

    last_check = models.DateTimeField(null=True, blank=True, unique=False)
    last_checkor = models.ForeignKey(User, blank=True, unique=False, null=True, on_delete=models.CASCADE, related_name="creator")

    def get_absolute_url(self):
        return reverse('taskflow:ticket', kwargs={'pk': self.pk})

    def run_workflow_step(self, context):
        """Run a single workflow step on this ticket.

        Can assume that the caller has a transaction lock on this ticket.
        """
        if self.last_check is None:
            # Never run on this one before
            element = Element.objects.get(workflow=self.workflow,
                                          is_initial=True)
            pre_task = Task(ticket=self,
                            element=element,
                            state=context.get('initial_arguments',{}),
                            creator=context['user'])
        else:
            # Not a brand-new ticket
            pre_task = Task.objects.filter(ticket=self).order_by('-creation')[0]
            element = pre_task.element

        task = element.process_task(pre_task, context)

        return task

    def run_workflow(self, context):
        """Run multiple workflow steps until no progress is made.

        This function assumes that the caller has a transaction lock on this ticket
        """
        self.last_checkor = context['user']
        last_task = None
        while True:
            task = self.run_workflow_step(context)
            self.last_check = now()
            if task is None:
                self.save()
                if last_task is not None:
                    last_task.save()
                return last_task
            last_task = task
            last_task.save()

    def __str__(self):
        return f"TK:{self.pk}:{self.creation}"


class TicketAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'creation', 'creator', 'last_check', 'last_checkor']
    list_filter = ['last_check', 'creation', 'workflow', 'creator', 'last_checkor']

    def run_workflow_step(self, request, queryset):
        context = Workflow.request_context(request)
        for q in queryset.all():
            t = q.run_workflow_step(context)
            if t is not None:
                t.save()
                q.last_checkor = context['user']
                q.last_check = now()
                q.save()

    run_workflow_step.short_description = 'Run workflow step on ticket and save the resultant task'

    def run_workflow(self, request, queryset):
        context = Workflow.request_context(request)
        for q in queryset.all():
            q.run_workflow(context)

    run_workflow.short_description = 'Run workflow on ticket and save the resultant task'

    actions = [run_workflow, run_workflow_step, ]


class Step(models.Model):
    """Step in processing of a ticket"""
    ticket = models.ForeignKey(Ticket, blank=False, unique=False, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, blank=False, unique=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['ticket', 'element', 'creation'],
                                               name='workflow_step_uniqueness'),
                       ]


class StepAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'element', 'creation']
    list_filter = ['filter', 'element', ]


class Task(models.Model):
    """The current task for a ticket.

    The ticket is in the current element, and processing has been paused within the element.
    """

    class Status(models.IntegerChoices):
        NEW = 0
        WAITING = 1
        UPDATED = 2
        COMPLETED = 3
        ERROR = 4
        FINISHED = 5
        TERMINATED = 6

    ticket = models.ForeignKey(Ticket, blank=False, unique=False, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, blank=False, unique=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    state = JSONField(null=False, blank=False, unique=False)
    creator = models.ForeignKey(User, blank=False, unique=False, null=False, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=Status.choices,
                                              default=Status.NEW)

    def clone_task(self, context):
        return Task(ticket=self.ticket,
                    element=self.element,
                    state=self.state,
                    creator=context['user'])

    @staticmethod
    def empty_task(ticket, element, user):
        return Task(ticket=ticket,
                    element=element,
                    state={},
                    creator=user)

    def __str__(self):
        return f"{self.ticket}:{self.element}:{self.creation}"

    @classmethod
    def latest_tasks(cls, exclude_finished=True):
        sub_query = cls.objects.filter(ticket=OuterRef('ticket')).values('ticket').annotate(max_creation=Max('creation')).values_list('max_creation')
        qs = cls.objects.filter(creation=Subquery(sub_query))

        if exclude_finished:
            qs = qs.filter(~Q(status=Task.Status.FINISHED),
                           ~Q(status=Task.Status.TERMINATED))
        return qs

    def get_absolute_url(self):
        return reverse('taskflow:task', kwargs={'pk': self.pk})

    class Meta:
        constraints = [#models.CheckConstraint(check=Q(ticket__workflow=F('element__workflow')),
                       #                       name='workflow_element_ticket_equal'),
                       models.UniqueConstraint(fields=['ticket', 'creation'],
                                               name='workflow_task_uniqueness'),
                       ]


class TaskAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'element', 'creation', 'creator', 'status',]
    list_filter = ['status', 'creation', 'creator',]

    def run_task_step(self, request, queryset):
        context = Workflow.request_context(request)
        for q in queryset.all():
            t = q.ticket.run_workflow_step(context)
            if t is not None:
                t.save()
                q.ticket.last_checkor = context['user']
                q.ticket.last_check = now()
                q.ticket.save()

    run_task_step.short_description = "Run next workflow step on ticket associated with task"

    def run_task(self, request, queryset):
        context = Workflow.request_context(request)
        for q in queryset.all():
            q.ticket.run_workflow(context)

    run_task.short_description = "Run workflow for ticket associated with task"

    actions = [run_task_step, run_task, ]


class OperatorTask(models.Model):
    """Task requiring operator intervention"""
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    element = models.OneToOneField(Element, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True, blank=True, unique=False)
    operator = models.ForeignKey(User, blank=False, unique=False, null=False, on_delete=models.CASCADE)

    def progress_task(self):
        """Set state to done."""
        if self.completed is None:
            self.completed = datetime.datetime.now()
            self.save()

    def save(self, *args, **kwargs):
        ret = super().save(*args, **kwargs)
        if self.completed is not None:
            self.check_completed_tasks(Workflow.user_context(self.operator))
        return ret

    @staticmethod
    def check_completed_tasks(context):
        """Check all operator tasks for completed state that are still waiting"""
        comp_tasks = Task.latest_tasks().filter(status=Task.Status.WAITING)

        op_tasks = OperatorTask.objects.filter(ticket__task__in=comp_tasks,
                                               ticket__task__element=F('element'))

        for op_task in op_tasks:
            task = comp_tasks.get(ticket=op_task.ticket,
                                  element=op_task.element)
            new_task = task.clone_task(context)
            new_task.status = Task.Status.UPDATED
            new_task.save()


class OperatorTaskAdmin(admin.ModelAdmin):
    list_filter = ['created', 'completed', 'operator', 'element', ]
    list_display = ['ticket', 'element', 'created', 'completed', 'operator', ]

    def progress_task(self, request, queryset):
        context = Workflow.request_context(request)
        for q in queryset.all():
            q.progress_task()
            q.save()

    progress_task.short_description = "Progress operator task"

    actions = [progress_task, ]
