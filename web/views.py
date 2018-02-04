import json
from collections import defaultdict

from django.shortcuts import render

from crawler.tasks import get_user_information
from vector.tasks import get_similar_following_users


def index(request):
    return render(request, 'index.html')


def api(request):
    return render(request, 'api.html')


def user(request, target_user_acct):
    try:
        user_name, instance = target_user_acct.split("@")
        target_user = get_user_information(instance, user_name, False)
        target_user_following = set(json.loads(target_user.following))

        similar_users = [x for x in get_similar_following_users(target_user) if x[0] != target_user_acct]
        recommend_user_dict = defaultdict(float)
        for acct, sim in similar_users:
            user_name, instance = acct.split("@")
            u = get_user_information(instance, user_name, False)
            for recommend_acct in json.loads(u.following):
                if recommend_acct == target_user_acct:
                    continue
                if recommend_acct in target_user_following:
                    continue
                recommend_user_dict[recommend_acct] += sim

        context = {
            "recommend_users": [{
                "user_name": x[0].split("@")[0],
                "instance": x[0].split("@")[1],
                "similarity": x[1],
            } for x in list(sorted(recommend_user_dict.items(), key=lambda x: x[1], reverse=True))[:20]],
            "similar_users": [{
                "user_name": x[0].split("@")[0],
                "instance": x[0].split("@")[1],
                "similarity": x[1],
            } for x in similar_users]
        }
        return render(request, 'user.html', context)
    except ValueError as e:
        return render(request, 'error.html', {"message": str(e)}, status=404)

