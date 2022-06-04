from django.core.management import BaseCommand

from register.tasks import send_reminders


class Command(BaseCommand):
    help = 'Send reminders to signed-in users'

    def add_arguments(self, parser):
        parser.add_argument('--send', "-s", action="store_true")
        parser.add_argument('--template', "-t", nargs="?", type=str)

    def handle(self, *args, send, template, **options):
        send_reminders(send, template=template)