from datetime import timedelta

from dateutil.utils import today
from django.core.management import BaseCommand

from register.tasks import clean_old_records


class Command(BaseCommand):
    help = "Cleans old records"

    def add_arguments(self, parser):
        parser.add_argument("--days", "-d", type=int, default=30)

    def handle(self, *args, days, **options):
        clean_old_records(days=days)
