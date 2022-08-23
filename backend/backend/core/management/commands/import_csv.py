from django.core.management.base import BaseCommand

import csv

from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):

        with open('C:\\Dev\\foodgram-project-react\\data\\ingredients.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                 _, created = Ingredient.objects.get_or_create(
                     name=row[0],
                     measurement_unit=row[1],
                     )