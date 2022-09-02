from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        User.objects.create_superuser(
            'admin', 'admin@admin.admin', 'karamba03'
        )