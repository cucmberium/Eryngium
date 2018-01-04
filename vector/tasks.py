import pickle
import json

import numpy as np
import gensim
import MeCab

from django.conf import settings
from crawler.models import User


def calculate_word_vector(file_name):
    corpus = gensim.models.word2vec.Text8Corpus(file_name)
    model = gensim.models.Word2Vec(corpus, size=300, window=5, min_count=5, sample=1e-3,
                                   sg=1, hs=1, negative=5, workers=4)
    with open(settings.WORDVECTOR_PATH, 'wb') as f:
        pickle.dump(model, f)


def calculate_user_following_vector():
    users = User.objects.all()
    labeled_followings = []
    for user in users:
        following = json.loads(user.following)
        if not following:
            continue

        ls = gensim.models.doc2vec.LabeledSentence(words=following, tags=[user.user_name + "@" + user.instance])
        labeled_followings.append(ls)

    model = gensim.models.Doc2Vec(labeled_followings, size=300, window=8, min_count=1, workers=4)
    with open(settings.USERFOLLWINGVECTOR_PATH, 'wb') as f:
        pickle.dump(model, f)


def calculate_user_bio_vector():
    tagger = MeCab.Tagger("-d" + settings.MECAB_IPADIC_NEOLOGD_PATH)
    with open(settings.WORDVECTOR_PATH, 'rb') as f:
        model = pickle.load(f)

    user_bio_vector = {}
    users = User.objects.all()
    for user in users:
        key = user.user_name + "@" + user.instance

        cws = [m.split("\t")[0] for m in tagger.parse(json.loads(user.bio)).split("\n")
              if len(m.split("\t")) >= 2 and m.split("\t")[1].split(",")[0] == "名詞"]
        cwvs = [model.wv[cw] for cw in cws if cw in model.wv.vocab]
        if not cwvs:
            user_bio_vector[key] = np.zeros(300)
        else:
            user_bio_vector[key] = np.mean(cwvs)