from django.contrib import admin
from .models import Worker, Contract, Organization


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'category', 'availability_status', 'date_added')
    search_fields = ('name__username',)  # Assuming CustomUser has a 'username' field
    list_filter = ('availability_status',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('worker', 'organization_name', 'project_title', 'start_date', 'status')
    search_fields = ('project_title', 'worker__name__username')  # Assuming CustomUser has a 'username' field
    list_filter = ('status',)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone_number')
    search_fields = ('name', 'contact_person')
 