from django.contrib import admin
from django.contrib import admin
from .models import JobData
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class JobResource(resources.ModelResource):
    class Meta:
        model = JobData


class JobAdmin(ImportExportModelAdmin):
    resource_class = JobResource


admin.site.register(JobData, JobAdmin)
