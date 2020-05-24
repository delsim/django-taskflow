from django.contrib import admin


from .models import (Workflow, WorkflowAdmin,
                     Element, ElementAdmin,
                     Link, LinkAdmin,
                     Ticket, TicketAdmin,
                     Task, TaskAdmin,
                     Operation, OperationAdmin,
                     )


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Operation, OperationAdmin)
