from django.contrib import admin

from blood import models

admin.site.register(models.Donation)
admin.site.register(models.Patient)


class PercentageAdmin(admin.TabularInline):
    model = models.PopulationBloodTypePercentage


class PopulationAdmin(admin.ModelAdmin):
    inlines = [PercentageAdmin]


admin.site.register(models.PopulationBloodTypeDistribution, PopulationAdmin)

admin.site.register(models.MCIRequest)
admin.site.register(models.SingleRequest)
