from django.shortcuts import render
from django.http import HttpResponse

from crawler.tasks import get_user_information
from vector.tasks import get_similar_following_users


def index(request):
    return HttpResponse("testest")


def user(request, acct):
    user_name, instance = acct.split("@")
    u = get_user_information(instance, user_name)
    similar_user = get_similar_following_users(u)
    return HttpResponse([u + " : " + str(sim) + "<br>" for u, sim in similar_user])

