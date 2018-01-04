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
