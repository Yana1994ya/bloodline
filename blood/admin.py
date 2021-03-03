from django.contrib import admin

from blood import models

# Register your models here.
admin.site.register(models.Donation)
admin.site.register(models.Patient)


class PrecentageAdmin(admin.TabularInline):
    model = models.PopulationBloodTypePercentage


class PopulationAdmin(admin.ModelAdmin):
    inlines = [PrecentageAdmin]


admin.site.register(models.PopulationBloodTypeDistribution, PopulationAdmin)
