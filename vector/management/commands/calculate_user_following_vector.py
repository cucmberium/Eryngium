# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand

from vector.tasks import calculate_user_following_vector_batch


class Command(BaseCommand):
    help = 'Calculate user following vector using d2v'

    def handle(self, *args, **options):
        calculate_user_following_vector_batch()
