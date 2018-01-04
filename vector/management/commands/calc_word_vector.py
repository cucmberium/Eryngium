# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand

from vector.tasks import calculate_word_vector


class Command(BaseCommand):
    help = 'Calculate word vector using w2v'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        calculate_word_vector(file_name)
