import json
from collections import defaultdict
from urllib.parse import quote

from django.shortcuts import render
from django.urls import reverse

from crawler.tasks import get_user_information
from vector.tasks import get_similar_following_users
from crawler.models import UserInfo


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

        recommend_users = list(sorted(recommend_user_dict.items(), key=lambda x: x[1], reverse=True))[:20]
        target_user_name = [x[0].split("@")[0] for x in recommend_users] + [x[0].split("@")[0] for x in similar_users]
        userinfo_dict = {user_info.user_name + "@" + user_info.instance: user_info for user_info in
                         UserInfo.objects.filter(user_name__in=target_user_name)}

        share_text = f"@{target_user_acct}さんにおすすめのユーザー\n\n"
        for recommend_user in [x for x in recommend_users[:5] if x[0] in userinfo_dict]:
            share_text += f"{recommend_user[0]}\n" \
                          f"おすすめ度:{recommend_user[1]:.2f}\n"
        share_text += "\n"
        share_text += "Mastodonおすすめユーザー検索\n"
        share_text += request.build_absolute_uri(reverse('index'))
        share_url = f"https://{instance}/share?text={quote(share_text, safe='')}"

        context = {
            "target_user_accts": target_user_acct,
            "recommend_users": [{
                "acct": x[0],
                "display_name": json.loads(userinfo_dict[x[0]].display_name),
                "avatar": userinfo_dict[x[0]].avatar,
                "bio": json.loads(userinfo_dict[x[0]].note).replace('class="invisible"', ''),
                "url": userinfo_dict[x[0]].url,
                "similarity": x[1],
            } for x in recommend_users[:20] if x[0] in userinfo_dict],
            "similar_users": [{
                "acct": x[0],
                "display_name": json.loads(userinfo_dict[x[0]].display_name),
                "avatar": userinfo_dict[x[0]].avatar,
                "bio": json.loads(userinfo_dict[x[0]].note).replace('class="invisible"', ''),
                "url": userinfo_dict[x[0]].url,
                "similarity": x[1],
            } for x in similar_users if x[0] in userinfo_dict],
            "share_url": share_url
        }
        return render(request, 'user.html', context)
    except ValueError as e:
        return render(request, 'error.html', {"message": str(e)}, status=404)

