from django import forms

from blood import models
from blood.blood_types import AVAILABLE_TYPES_CHOICES


class IdSearch(forms.Form):
    id_number = forms.RegexField(required=True, regex="^\\d{10}$")


class PatientDetails(forms.Form):
    blood_type = forms.ChoiceField(choices=AVAILABLE_TYPES_CHOICES, required=True)
    birthday = forms.DateField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.RegexField("^0[\\d]{1,2}-[\\d]{7}$", required=False)
    smokes = forms.BooleanField(required=False)


class AcceptDonation(PatientDetails):
    units = forms.IntegerField(required=True)


class SingleRequestForm(PatientDetails):
    units = forms.IntegerField(required=True)


class MCIRequestForm(forms.Form):
    units = forms.IntegerField(required=True)
    distribution = forms.ModelChoiceField(models.BloodTypeDistribution.objects)
