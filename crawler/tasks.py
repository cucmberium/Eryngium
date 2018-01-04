import datetime
import time
import requests
import re
import json

from crawler.models import User


def crawl_user_from_timeline(instance, access_tokens):
    headers = {
        'User-Agent': 'Eryngium',
        'Authorization': 'Bearer ' + access_tokens
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
