from django.db import models
from django.db.models import Q, F

from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.text import slugify
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


class OperationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'function']


class Workflow(NameSlugBase):
    description = models.TextField()

    def get_absolute_url(self):
        return reverse(f"{app_name}:workflow", kwargs={'slug': self.slug})

    @staticmethod
    def request_context(request):
        """Form a context from the curent request."""
        context = {'user': request.user,
                   }
        return context

    def create_ticket(self, context):
        t = Ticket(workflow=self,
                   creator=context['user'])
        return t


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]

    def create_ticket(self, request, queryset):
        for q in queryset.all():
            context = Workflow.request_context(request)
            ticket = q.create_ticket(context)
            ticket.save()
            ticket.run_workflow(context)

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


class ElementAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'operation', 'slug_name', 'is_initial',]
    list_filter = ['is_initial', 'operation', 'workflow',]


class Link(models.Model):
    source = models.ForeignKey(Element, blank=False, unique=False, null=False, on_delete=models.CASCADE, related_name="dtflow_link_source")
    target = models.ForeignKey(Element, blank=False, unique=False, null=False, on_delete=models.CASCADE, related_name="dtflow_link_target")
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

    def run_workflow(self, context):
        pass

    def __str__(self):
        return f"TK:{self.pk}:{self.creation}"


class TicketAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'creation', 'creator',]
    list_filter = ['creation', 'workflow', 'creator']


class Task(models.Model):
    """The current task for a ticket.

    The ticket is in the current element, and processing has been paused within the element.
    """
    ticket = models.ForeignKey(Ticket, blank=False, unique=False, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, blank=False, unique=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    state = JSONField(null=False, blank=False, unique=False)
    creator = models.ForeignKey(User, blank=False, unique=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ticket}:{self.element}:{self.creation}"

    class Meta:
        constraints = [#models.CheckConstraint(check=Q(ticket__workflow=F('element__workflow')),
                       #                       name='workflow_element_ticket_equal'),
                       models.UniqueConstraint(fields=['ticket', 'creation'],
                                               name='workflow_task_uniqueness'),
                       ]


class TaskAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'element', 'creation', 'creator', ]
    list_filter = ['creation', 'creator', ]
