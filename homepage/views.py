from csv import writer
import io
from io import StringIO

from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render
from reversion.models import Version

from blood.models import OutstandingDonations


def homepage(request):
    audit_trail = []

    if request.user.is_authenticated and request.user.is_superuser:
        audit_trail = Version.objects.select_related().order_by("-revision__date_created")[0:10]

    outstanding = OutstandingDonations.objects \
        .values('blood_type') \
        .annotate(outstanding=Sum('units')) \
        .order_by('blood_type')

    return render(request, "homepage.html", {
        "outstanding": outstanding,
        "audit_trail": audit_trail
    })


def export_stats(request):
    b = StringIO()

    w = writer(b, delimiter='\t')
    w.writerow(["blood_type", "outstanding_count"])

    outstanding = OutstandingDonations.objects \
        .values('blood_type') \
        .annotate(outstanding=Sum('units')) \
        .order_by('blood_type')

    for blood_type in outstanding:
        w.writerow([
            blood_type['blood_type'],
            blood_type['outstanding']
        ])

    b.seek(0, io.SEEK_SET)

    return HttpResponse(
        b,
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="stats.csv"'},
    )


def export_audit_trail(request):
    if request.user.is_anonymous or not request.user.is_superuser:
        raise Http404("Only superuser allowed to export")

    b = StringIO()

    w = writer(b, delimiter='\t')
    w.writerow(["object_id", "format", "serialized_data", "object_repr", "content_type",
                "date_created", "comment", "user_id", "user_first_name",
                "user_last_name", "user_email"])

    for record in Version.objects.select_related():
        if record.revision.user:
            user_fields = [
                record.revision.user_id,
                record.revision.user.first_name,
                record.revision.user.last_name,
                record.revision.user.email
            ]
        else:
            user_fields = ["", "", "", ""]

        w.writerow([
                       record.object_id,
                       record.format,
                       record.serialized_data,
                       record.object_repr,
                       record.content_type.model,
                       record.revision.date_created.isoformat(),
                       record.revision.comment,
                   ] + user_fields)
    b.seek(0, io.SEEK_SET)

    return HttpResponse(
        b,
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="audit_trail.csv"'},
    )
