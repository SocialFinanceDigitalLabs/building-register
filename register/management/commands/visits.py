from pathlib import Path

import tablib
from django.core.management import BaseCommand
from django.db.models import Count, Q, Min, Max, Case, When, F, Value
from django.utils.timezone import make_naive as django_make_naive

from register.models import SignInRecord
from register.util.tablib import output_tablib


def make_naive(date):
    if date is not None:
        return django_make_naive(date)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('output', type=str, default='-', help='Output file', nargs='?')
        parser.add_argument('--summary', '-s', action='store_true', help='Show summary')

    def handle(self, *args, output, summary, **options):
        query = SignInRecord.objects.values(
            'user__username', 'date'
        ).annotate(
            min_sign_in=Min('sign_in__timestamp'),
            max_sign_out=Max('sign_out__timestamp'),
            last_orphan_sign_in=Max('sign_in__timestamp', filter=Q(sign_out__isnull=True)),
        ).annotate(
            max_sign_out=Case(
                When(last_orphan_sign_in__gt=F('max_sign_out'), then=Value(None)),
                default=F('max_sign_out'),
            )
        )

        ds = tablib.Dataset(headers=('user', 'date', 'sign_in', 'sign_out'), title='Records')
        for record in query.order_by('user', 'date'):
            ds.append((
                record['user__username'],
                record['date'],
                make_naive(record['min_sign_in']),
                make_naive(record['max_sign_out']),
            ))

        if summary:
            summary_query = query.values('user__username').annotate(
                days_signed_in=Count('date'),
                days_not_signed_out=Count('date', filter=Q(sign_out__isnull=True)),
            )
            ds_summary = tablib.Dataset(headers=('user', 'days_signed_in', 'days_not_signed_out', 'pct'),
                                        title='Summary')
            for record in summary_query.order_by('user'):
                ds_summary.append((
                    record['user__username'],
                    record['days_signed_in'],
                    record['days_not_signed_out'],
                    100 * record['days_not_signed_out'] / record['days_signed_in']
                ))
            ds = tablib.Databook((ds, ds_summary))

        output_tablib(ds, output)


