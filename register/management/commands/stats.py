from pathlib import Path

import tablib
from django.core.management import BaseCommand
from django.db.models import Count, Q

from register.models import SignInRecord
from register.util.tablib import output_tablib


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('output', type=str, default='-', help='Output file', nargs='?')

    def handle(self, *args, output, **options):
        query = SignInRecord.objects.values(
            'date'
        ).annotate(
            distinct_users=Count('user_id', distinct=True),
            not_signed_out=Count('user_id', filter=Q(sign_out__isnull=True))
        ).order_by('date')

        ds = tablib.Dataset(headers=('date', 'distinct_users', 'not_signed_out'))
        for record in query:
            ds.append((record['date'], record['distinct_users'], record['not_signed_out']))

        output_tablib(ds, output)

