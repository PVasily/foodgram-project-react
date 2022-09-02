import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

root_path = os.path.dirname(os.path.dirname(settings.BASE_DIR))
data_path = os.path.join(root_path, 'data', 'ingredients.csv')


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        with open(data_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = Ingredient.objects.get_or_create(
                                                    name=row[0],
                                                    measurement_unit=row[1])
