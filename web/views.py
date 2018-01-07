from django.shortcuts import render

from crawler.tasks import get_user_information
from vector.tasks import get_similar_following_users


def index(request):
    return render(request, 'index.html')


def api(request):
    return render(request, 'index.html')


def user(request, acct):
    user_name, instance = acct.split("@")
    u = get_user_information(instance, user_name)
    similar_users = get_similar_following_users(u)
    context = {
        "similar_users": [{
            "user_name": u[0].split("@")[0],
            "instance": u[0].split("@")[1],
            "similarity": u[1],
        } for u in similar_users]
    }
    return render(request, 'user.html', context)

