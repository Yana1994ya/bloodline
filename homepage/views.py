from django.db.models import Sum
from django.shortcuts import render

from blood.models import OutstandingDonations


def homepage(request):
    outstanding = OutstandingDonations.objects \
        .values('blood_type') \
        .annotate(outstanding=Sum('units')) \
        .order_by('blood_type')

    return render(request, "homepage.html", {"outstanding": outstanding})
