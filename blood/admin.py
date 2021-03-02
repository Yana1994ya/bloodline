from django.contrib import admin
from blood import models

# Register your models here.
admin.site.register(models.Donation)
admin.site.register(models.Patient)
