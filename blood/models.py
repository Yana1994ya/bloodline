from datetime import datetime
from math import ceil
import re
from typing import List, Optional, Tuple, Type

from django.contrib.contenttypes.models import ContentType
from django.db import models

from blood.blood_types import AVAILABLE_TYPES_CHOICES, POPULATION_BLOOD_TYPE_DISTRIBUTION


class InvalidPatientId(Exception):
    def __init__(self, patient_id):
        self.patient_id = patient_id


class Patient(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)

    birthday = models.DateField()

    blood_type = models.CharField(max_length=10, choices=AVAILABLE_TYPES_CHOICES)

    smokes = models.BooleanField()
    phone_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"({self.id}) {self.first_name} {self.last_name}"

    def update(
            self,
            first_name: str,
            last_name: str,
            birthday: datetime.date,
            blood_type: str,
            smokes: bool,
            phone_number: Optional[str]
    ):
        if not (
                first_name == self.first_name and
                last_name == self.last_name and
                birthday == self.birthday and
                blood_type == self.blood_type and
                smokes == self.smokes and
                phone_number == self.phone_number
        ):
            self.first_name = first_name
            self.last_name = last_name
            self.birthday = birthday
            # Blood type is a major change, ask for confirmation
            self.blood_type = blood_type
            self.smokes = smokes
            self.phone_number = phone_number

            self.save()

    @property
    def initial_data(self) -> dict:
        return {
            "blood_type": self.blood_type,
            "birthday": self.birthday,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "smokes": self.smokes,
            "phone_number": self.phone_number
        }

    @classmethod
    def details(cls, id_number: str) -> Tuple['Patient', dict]:
        if not re.fullmatch("^\\d{10}$", id_number):
            raise InvalidPatientId(id_number)

        try:
            patient = cls.objects.get(id=id_number)
            return patient, patient.initial_data
        except cls.DoesNotExist:
            patient = cls(id=id_number)
            return patient, {}


class Donation(models.Model):
    id = models.AutoField(primary_key=True)

    donor = models.ForeignKey(Patient, on_delete=models.CASCADE)

    units = models.IntegerField()

    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.blood_type} {self.units} units"

    @property
    def blood_type(self) -> str:
        return self.donor.blood_type


class OutstandingDonations(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, primary_key=True)
    units = models.IntegerField()
    blood_type = models.CharField(max_length=10, choices=AVAILABLE_TYPES_CHOICES)
    donation_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "blood_outstanding_donations"


class OutstandingDonationsMCI(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, primary_key=True)
    units = models.IntegerField()
    blood_type = models.CharField(max_length=10, choices=AVAILABLE_TYPES_CHOICES)
    donation_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "blood_outstanding_donations_mci"


class BloodRank(models.Model):
    blood_type = models.CharField(
        primary_key=True,
        max_length=10,
        choices=AVAILABLE_TYPES_CHOICES
    )
    rank = models.IntegerField()

    class Meta:
        managed = False
        db_table = "blood_rank"


class IssueRequest(models.Model):
    id = models.AutoField(primary_key=True)

    content_type = models.ForeignKey(
        ContentType,
        editable=False,
        null=True,
        on_delete=models.CASCADE
    )

    request_time = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        super(IssueRequest, self).save(*args, **kwargs)


class SingleRequest(IssueRequest):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    units = models.IntegerField()

    def __str__(self):
        return f"Single request {self.units} Units of {self.patient.blood_type}"


class BloodTypeDistribution(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)

    dist_type = models.CharField(
        max_length=10,
        editable=False,
        null=False,
        choices=[
            (POPULATION_BLOOD_TYPE_DISTRIBUTION, POPULATION_BLOOD_TYPE_DISTRIBUTION)
        ]
    )

    def save(self, *args, **kwargs):
        if self.dist_type is None:
            self.dist_type = self.distribution_type()

            if self.dist_type is None:
                raise Exception("no dist_type set")

        super(BloodTypeDistribution, self).save(*args, **kwargs)

    @property
    def cls(self) -> Type['BloodTypeDistribution']:
        if self.dist_type == POPULATION_BLOOD_TYPE_DISTRIBUTION:
            return PopulationBloodTypeDistribution
        else:
            raise Exception("Encountered unfamiliar distribution type:self.dist_type")

    @property
    def leaf(self) -> 'BloodTypeDistribution':
        return self.cls.objects.get(id=self.id)

    @classmethod
    def distribution_type(cls) -> str:
        raise Exception("distribution_type called on abstract base class")

    @classmethod
    def query_required(cls) -> bool:
        return False

    def blood_types(self, total_units: int) -> List[Tuple[str, int]]:
        if self.cls.query_required:
            return self.leaf.blood_types(total_units)
        else:
            return self.cls.blood_types(self, total_units)

    def __str__(self):
        return self.cls.__str__(self)


class PopulationBloodTypeDistribution(BloodTypeDistribution):

    def blood_types(self, total_units: int) -> List[Tuple[str, int]]:
        result = []

        for p in PopulationBloodTypePercentage.objects.filter(distribution=self):
            result.append((p.blood_type, ceil(float(total_units) * float(p.percentage) / 100.0)))

        return result

    @classmethod
    def distribution_type(cls) -> str:
        return POPULATION_BLOOD_TYPE_DISTRIBUTION

    def __str__(self):
        return f"Population: {self.name}"


class PopulationBloodTypePercentage(models.Model):
    distribution = models.ForeignKey(
        PopulationBloodTypeDistribution,
        on_delete=models.CASCADE
    )

    blood_type = models.CharField(
        max_length=10,
        choices=AVAILABLE_TYPES_CHOICES
    )

    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = (("distribution_id", "blood_type"))


class MCIRequest(IssueRequest):
    units = models.IntegerField()
    distribution = models.ForeignKey(BloodTypeDistribution, on_delete=models.CASCADE)

    def __str__(self):
        return f"MCIRequest for {self.units} with {self.distribution} distribution"

    class Meta:
        verbose_name = "MCI Request"


class Issue(models.Model):
    request = models.ForeignKey(IssueRequest, on_delete=models.CASCADE)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    request_blood_type = models.CharField(max_length=10, choices=AVAILABLE_TYPES_CHOICES)
    units = models.IntegerField()

    @property
    def blood_type(self) -> str:
        return self.donation.blood_type


class Reject(models.Model):
    time = models.DateTimeField(auto_now_add=True, editable=False)

    request_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )


class RejectType(models.Model):
    reject = models.ForeignKey(Reject, on_delete=models.CASCADE)

    blood_type = models.CharField(
        max_length=10,
        choices=AVAILABLE_TYPES_CHOICES
    )

    units = models.IntegerField()
