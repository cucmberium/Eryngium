import json

from django.db import models
from django.utils import timezone


class User(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    instance = models.CharField(db_column='instance', db_index=True, max_length=120, blank=False, null=False)
    user_id = models.BigIntegerField(db_column='user_id', db_index=True, null=False)
    user_name = models.CharField(db_column='user_name', db_index=True, max_length=120, blank=False, null=False)
    following = models.TextField(db_column='following', null=False)
    toots = models.TextField(db_column='toots', null=False)
    bio = models.TextField(db_column='bio', null=False)
    created_at = models.DateTimeField(db_column='created_at', default=timezone.now)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        managed = True
        db_table = 'users'


class UserInfo(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    instance = models.CharField(db_column='instance', db_index=True, max_length=120, blank=False, null=False)
    user_name = models.CharField(db_column='user_name', db_index=True, max_length=120, blank=False, null=False)
    display_name = models.CharField(db_column='display_name', max_length=120, blank=False, null=False)
    locked = models.BooleanField(db_column='locked', default=False)
    followers_count = models.IntegerField(db_column='followers_count', default=0)
    following_count = models.IntegerField(db_column='following_count', default=0)
    statuses_count = models.IntegerField(db_column='statuses_count', default=0)
    note = models.TextField(db_column='bio', null=False)
    url = models.TextField(db_column='url', null=False)
    avatar = models.TextField(db_column='avatar', null=False)
    avatar_static = models.TextField(db_column='avatar_static', null=False)
    header = models.TextField(db_column='header', null=False)
    header_static = models.TextField(db_column='header_static', null=False)
    moved = models.TextField(db_column='moved', default=False)
    created_at = models.DateTimeField(db_column='created_at', default=timezone.now)

    class Meta:
        managed = True
        db_table = 'user_info'

    @classmethod
    def create_or_update(cls, account, instance):
        user_info, created = UserInfo.objects.get_or_create(instance=instance, user_name=account["username"])
        user_info.instance = instance
        user_info.user_name = account["username"]
        user_info.display_name = account["display_name"]
        user_info.locked = account["locked"]
        user_info.followers_count = account["followers_count"]
        user_info.following_count = account["following_count"]
        user_info.statuses_count = account["statuses_count"]
        user_info.note = json.loads(account["note"])
        user_info.url = account["url"]
        user_info.avatar = account["avatar"]
        user_info.avatar_static = account["avatar_static"]
        user_info.header = account["header"]
        user_info.header_static = account["header_static"]
        user_info.moved = account["moved"] if "moved" in account else False
        user_info.created_at = account["created_at"]
        user_info.save()
