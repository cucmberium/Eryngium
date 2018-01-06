import datetime
import time
import requests
import re
import json

from django.conf import settings
from crawler.models import User


def crawl_user_from_timeline(instance):
    if instance not in settings.ACCESSTOKEN_SETTING:
        raise ValueError(instance + " is not supported")

    headers = {
        'User-Agent': 'Eryngium',
        'Authorization': 'Bearer ' + settings.ACCESSTOKEN_SETTING[instance]
    }

    response = requests.get(f'https://{instance}/api/v1/timelines/public?local=true&limit=40', headers=headers)
    statuses = response.json()

    user_id_to_user_name = {int(status["account"]["id"]): status["account"]["username"] for status in statuses}
    user_id_to_bio = {int(status["account"]["id"]):
                      re.sub(r"<[^>]*?>", "", status["account"]["note"]) for status in statuses}

    user_ids = list(set([int(status["account"]["id"]) for status in statuses]))
    users = User.objects.filter(user_id__in=user_ids, instance=instance,
                                updated_at__gte=datetime.datetime.now() - datetime.timedelta(weeks=4))
    for user_id in set(user_ids) - set([user.user_id for user in users]):
        # Get user recent following
        response = requests.get(f'https://{instance}/api/v1/accounts/{user_id}/following?limit=80', headers=headers)
        accts = [account["acct"] if "@" in account["acct"] else account["acct"] + "@" + instance
                 for account in response.json()]

        # Get user recent toot
        response = requests.get(f'https://{instance}/api/v1/accounts/{user_id}/statuses?limit=40', headers=headers)
        statuses = [re.sub(r"<[^>]*?>", "", status["content"]) for status in response.json()]

        # Save or update user object
        user, created = User.objects.get_or_create(instance=instance, user_id=user_id)
        user.instance = instance
        user.user_id = user_id
        user.user_name = user_id_to_user_name[user_id]
        user.following = json.dumps(accts)
        user.toots = json.dumps(statuses)
        user.bio = json.dumps(user_id_to_bio[user_id])
        user.save()

        time.sleep(1)


def get_user_information(instance, user_name):
    user = User.objects.filter(user_name=user_name, instance=instance).first()
    if user is not None:
        return user

    if instance not in settings.ACCESSTOKEN_SETTING:
        raise ValueError(f"{instance} is not supported")

    headers = {
        'User-Agent': 'Eryngium',
        'Authorization': 'Bearer ' + settings.ACCESSTOKEN_SETTING[instance]
    }

    params = {
        "q": user_name + "@" + instance
    }
    response = requests.get(f'https://{instance}/api/v1//api/v1/search', params=params, headers=headers)
    accounts = response.json()["accounts"]
    if len(accounts) == 0:
        raise ValueError(f"User {user_name}@{instance} is not found")

    target_user_id = accounts[0]["id"]
    target_user_bio = accounts[0]["note"]
    # Get user recent following
    response = requests.get(f'https://{instance}/api/v1/accounts/{user_id}/following?limit=80', headers=headers)
    accts = [account["acct"] if "@" in account["acct"] else account["acct"] + "@" + instance
             for account in response.json()]

    # Get user recent toot
    response = requests.get(f'https://{instance}/api/v1/accounts/{user_id}/statuses?limit=40', headers=headers)
    statuses = [re.sub(r"<[^>]*?>", "", status["content"]) for status in response.json()]

    # Save or update user object
    user, created = User.objects.get_or_create(instance=instance, user_id=target_user_id)
    user.instance = instance
    user.user_id = target_user_id
    user.user_name = user_name
    user.following = json.dumps(accts)
    user.toots = json.dumps(statuses)
    user.bio = json.dumps(target_user_bio)
    user.save()

    return user
