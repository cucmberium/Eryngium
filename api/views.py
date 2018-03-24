import json
from collections import defaultdict

from django.http import JsonResponse

from crawler.tasks import get_user_information
from vector.tasks import get_similar_following_users
# Create your views here.


def recommendations(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    target_user_acct = request.GET.get("acct")
    if target_user_acct is None or "@" not in target_user_acct:
        return JsonResponse({'error': 'parameter acct is required'}, status=400)

    try:
        user_name, instance = target_user_acct.split("@")
        target_user = get_user_information(instance, user_name, False)
        target_user_following = set(json.loads(target_user.following))

        sim_users = [x for x in get_similar_following_users(target_user) if x[0] != target_user_acct]
        recommend_user_dict = defaultdict(float)
        for acct, sim in sim_users:
            user_name, instance = acct.split("@")
            u = get_user_information(instance, user_name, False)
            for recommend_acct in json.loads(u.following):
                if recommend_acct == target_user_acct:
                    continue
                if recommend_acct in target_user_following:
                    continue
                recommend_user_dict[recommend_acct] += sim

        return JsonResponse(
            [{"acct": x[0], "similarity": x[1]}
             for x in list(sorted(recommend_user_dict.items(), key=lambda x: x[1], reverse=True))[:20]],
            safe=False
        )

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=404)


def similar_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    target_user_acct = request.GET.get("acct")
    if target_user_acct is None or "@" not in target_user_acct:
        return JsonResponse({'error': 'parameter acct is required'}, status=400)

    try:
        user_name, instance = target_user_acct.split("@")
        target_user = get_user_information(instance, user_name, False)

        sim_users = [x for x in get_similar_following_users(target_user) if x[0] != target_user_acct]
        return JsonResponse(
            [{"acct": x[0], "similarity": x[1]}
             for x in sim_users],
            safe=False
        )

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=404)
