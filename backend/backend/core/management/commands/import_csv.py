import csv
import os

from backend.settings import BASE_DIR
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

p = os.path.dirname(os.path.dirname(BASE_DIR))
path = os.path.join(p, 'data', 'ingredients.csv')


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):

        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = Ingredient.objects.get_or_create(
                                                    name=row[0],
                                                    measurement_unit=row[1])
