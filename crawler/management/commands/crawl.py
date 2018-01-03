# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand

from crawler.tasks import crawl_user_from_timeline


class Command(BaseCommand):
    help = 'Crawl public timeline of Mastodon instance'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('tokens', type=str)

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        instance = options['name']
        access_tokens = options['tokens']
        crawl_user_from_timeline(instance, access_tokens)
