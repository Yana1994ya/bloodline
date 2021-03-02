from django.db import models
from blood.blood_types import AVAILABLE_TYPES_CHOICES


class Patient(models.Model):
	id = models.CharField(max_length=10, primary_key=True)
	first_name = models.CharField(max_length=250)
	last_name = models.CharField(max_length=250)

	birthday = models.DateField()

	blood_type = models.CharField(max_length=10, choices=AVAILABLE_TYPES_CHOICES)

	def __str__(self):
		return f"({self.id}) {self.first_name} {self.last_name}"


# Create your models here.
class Donation(models.Model):
	id = models.AutoField(primary_key=True)

	donor = models.ForeignKey(Patient, on_delete=models.CASCADE)

	units = models.IntegerField()

	donation_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.donor.blood_type} {self.units} units"