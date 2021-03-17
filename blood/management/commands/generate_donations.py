from datetime import datetime, timedelta
from random import choice, randint, randrange

from django.core.management.base import BaseCommand
from django.db import transaction
import faker

from blood import blood_types, models


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


class Command(BaseCommand):
    help = 'Displays current time'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int,
                            help='Indicates the number of donations to be created')

    @transaction.atomic
    def generate_donation(self):
        id_number = choice("123456789")
        for _ in range(0, 8):
            id_number += choice("1234567890")

        f = faker.Faker()

        first_name, _, last_name = f.name().partition(" ")

        phone_number = None
        if randint(0, 10) < 8:
            phone_number = choice(
                ("054", "08", "03", "07", "02")
            ) + "-" + choice("123456789")

            for _ in range(0, 7):
                phone_number += choice("1234567890")

        p = models.Patient(
            id=id_number,
            first_name=first_name,
            last_name=last_name,
            blood_type=choice(blood_types.AVAILABLE_TYPES),
            smokes=randint(0, 10) >= 8,
            phone_number=phone_number,
            birthday=f.date_of_birth()
        )

        p.save()

        d = models.Donation(
            donor=p,
            units=randint(1, 3),
            donation_date=random_date(datetime.now() - timedelta(days=12), datetime.now())
        )

        d.save()

    def handle(self, *args, **kwargs):
        donations = kwargs["total"]

        for _ in range(1, donations):
            self.generate_donation()
