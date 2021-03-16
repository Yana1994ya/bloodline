from typing import List, Tuple, Type

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from blood.blood_types import compatible_blood_types
from blood.models import BloodTypeDistribution, Issue, IssueRequest, MCIRequest, \
    OutstandingDonations, OutstandingDonationsMCI, Patient, \
    Reject, RejectType, SingleRequest


class CanNotFulfill(Exception):
    def __init__(self, missing_units: List[Tuple[str, int]]):
        self.missing_units = missing_units

    @transaction.atomic
    def save_reject(self, request_type: Type[IssueRequest]):
        reject = Reject(
            request_type=ContentType.objects.get_for_model(request_type)
        )
        reject.save()

        for blood_type, units in self.missing_units:
            RejectType(
                reject=reject,
                blood_type=blood_type,
                units=units
            ).save()

        return reject


@transaction.atomic
def create_and_fill_single_request(patient: Patient, units: int) -> SingleRequest:
    request = SingleRequest(patient=patient, units=units)

    request.save()

    # try to fulfil the request
    fill_single_request(request)

    return request


@transaction.atomic
def create_and_fill_mci_request(distribution: BloodTypeDistribution, units: int) -> MCIRequest:
    request = MCIRequest(distribution=distribution, units=units)

    request.save()

    fill_mci_request(request)
    return request


def fill_single_request(single_request: SingleRequest):
    units_left = single_request.units
    donations = []

    while units_left > 0:
        if not donations:
            donations = list(OutstandingDonations.objects.filter(
                blood_type__in=compatible_blood_types(single_request.patient.blood_type)
            )[0:10])

            if not donations:
                raise CanNotFulfill([(single_request.patient.blood_type, units_left)])

        donation = donations.pop()

        issue_units = min(donation.units, units_left)

        Issue(
            request=single_request,
            donation_id=donation.donation_id,
            request_blood_type=single_request.patient.blood_type,
            units=issue_units
        ).save()

        units_left -= issue_units


def fill_mci_request(request: MCIRequest):
    missing_units = []

    for blood_type, units_left in request.distribution.blood_types(request.units):
        donations = []

        while units_left > 0:
            if not donations:
                donations = list(OutstandingDonationsMCI.objects.filter(
                    blood_type__in=compatible_blood_types(blood_type)
                ).order_by("donation_date")[0:10])

                if not donations:
                    missing_units.append((blood_type, units_left))
                    break

            donation = donations.pop()

            issue_units = min(donation.units, units_left)

            Issue(
                request=request,
                donation_id=donation.donation_id,
                request_blood_type=blood_type,
                units=issue_units
            ).save()

            units_left -= issue_units

    if missing_units:
        raise CanNotFulfill(missing_units)
