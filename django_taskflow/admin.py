from django.contrib import admin


from .models import (Workflow, WorkflowAdmin,
                     Element, ElementAdmin,
                     Ticket, TicketAdmin,
                     Task, TaskAdmin,
                     )


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Task, TaskAdmin)

