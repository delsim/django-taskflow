from django.db import models
from django.db.models import Q, F

from django.contrib import admin
from django.urls import reverse
from django.utils.text import slugify

from .app_name import app_name


class Workflow(models.Model):
    name = models.CharField(max_length=100, unique=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def get_absolute_url(self):
        return reverse(f"{app_name}:workflow", kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug is None:
            pslug = slugify(self.slug)
            psc = Workflow.objects.filter(slug__startswith=pslug).count()
            if psc > 0:
                self.slug = f"{pslug}{psc}"
            else:
                self.slug = psc
        return super().save(*args, **kwargs)


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]


class Element(models.Model):
    workflow = models.ForeignKey(Workflow, blank=False, unique=False, on_delete=models.CASCADE)
    slug_name = models.SlugField(max_length=100, unique=False)
    is_initial = models.BooleanField(default=False, unique=False, null=False)

    def __str__(self):
        return f"{self.workflow}:{self.slug_name}"

    class Meta:
        constraints = [models.UniqueConstraint(fields=['workflow', 'slug_name'], name="uniqueness_workflow_slug"),
                       models.UniqueConstraint(fields=['workflow'], condition=Q(is_initial=True), name="unique_initial_element"),
                       ]


class ElementAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'slug_name', 'is_initial',]
    list_filter = ['is_initial', 'workflow',]


class Ticket(models.Model):
    workflow = models.ForeignKey(Workflow, blank=False, unique=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TK:{self.pk}:{self.creation}"


class TicketAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'creation']
    list_filter = ['creation', 'workflow']


class Task(models.Model):
    ticket = models.ForeignKey(Ticket, blank=False, unique=False, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, blank=False, unique=False, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket}:{self.element}:{self.creation}"

    class Meta:
        constraints = [#models.CheckConstraint(check=Q(ticket__workflow=F('element__workflow')),
                       #                       name='workflow_element_ticket_equal'),
                       models.UniqueConstraint(fields=['ticket', 'creation'],
                                               name='workflow_task_uniqueness'),
                       ]


class TaskAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'element', 'creation']
    list_filter = ['creation',]
