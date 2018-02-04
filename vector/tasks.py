import pickle
import json
import re

import numpy as np
import gensim
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer

from django.conf import settings
from crawler.models import User


mecab_tagger = MeCab.Tagger("-d" + settings.MECAB_IPADIC_NEOLOGD_PATH + " --unk-feature 未知語")

word_vector_model = None
user_following_vector_model = None
user_bio_vector_model = None


def get_similar_following_users(user, topn=20):
    global user_following_vector_model
    if user_following_vector_model is None:
        user_following_vector_model = pickle.load(open(settings.USERFOLLWINGVECTOR_PATH, 'rb'))

    if user.user_name + "@" + user.instance in user_following_vector_model:
        vector = user_following_vector_model[user.user_name + "@" + user.instance]
    else:
        vector = user_following_vector_model.infer_vector(doc_words=json.loads(user.following), steps=2000)
    return user_following_vector_model.docvecs.most_similar([vector], topn=topn)


def get_similar_bio_users(user, topn=10):
    global user_bio_vector_model
    if user_bio_vector_model is None:
        user_bio_vector_model = pickle.load(open(settings.USERBIOVECTOR_PATH, 'rb'))

    vec = calculate_user_bio_vector(user)
    dists = (1 + np.dot(user_bio_vector_model["syn0norm"], vec)) / 2
    best = gensim.matutils.argsort(dists, topn=topn, reverse=True)
    return [(user_bio_vector_model["index2word"][idx], float(dists[idx])) for idx in best]


def calculate_user_bio_vector(user):
    global word_vector_model, user_bio_vector_model
    if word_vector_model is None:
        word_vector_model = pickle.load(open(settings.WORDVECTOR_PATH, 'rb'))

    user_bio_tfidf = user_bio_vector_model["tfidf"].transform(
        [" ".join(get_content_words(json.loads(user.bio)))]).toarray()[0]
    best = gensim.matutils.argsort(user_bio_tfidf, topn=5, reverse=True)
    cws = [user_bio_vector_model["tfidf"].get_feature_names()[idx] for idx in best if user_bio_tfidf[idx] != 0]
    cwvs = [word_vector_model["syn0norm"][word_vector_model["word2index"][cw]]
            for cw in cws if cw in word_vector_model["word2index"]]

    if not cwvs:
        return np.zeros(200)
    else:
        return np.mean(cwvs, axis=0)


def get_content_words(text):
    content_words = []
    for m in mecab_tagger.parse(re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)",
                                       "", text)).split("\n"):
        if len(m.split("\t")) <= 1:
            continue

        word, data = m.split("\t")
        if data.split(",")[0] != "名詞":
            continue

        content_words.append(word)
    return content_words


def calculate_word_vector_batch(file_name):
    global word_vector_model
    corpus = gensim.models.word2vec.Text8Corpus(file_name)
    model = gensim.models.Word2Vec(corpus, size=200, window=5, min_count=5, sample=1e-3,
                                   sg=1, hs=0, negative=5, workers=4)
    model.init_sims()
    word_vector_model = {
        "index2word": model.wv.index2word,
        "word2index": {word: model.wv.vocab[word].index for word in model.wv.vocab},
        "syn0norm": model.wv.syn0norm
    }

    with open(settings.WORDVECTOR_PATH, 'wb') as f:
        pickle.dump(word_vector_model, f)


def calculate_user_following_vector_batch():
    global user_following_vector_model
    users = User.objects.all()
    labeled_followings = []
    for user in users:
        following = json.loads(user.following)
        if len(following) <= 1:
            continue
        ls = gensim.models.doc2vec.LabeledSentence(words=following, tags=[user.user_name + "@" + user.instance])
        labeled_followings.append(ls)

    user_following_vector_model = gensim.models.Doc2Vec(labeled_followings, size=300, window=5, dm=1,
                                                        min_count=1, workers=4, iter=1000, negative=5, sample=1e-6)
    with open(settings.USERFOLLWINGVECTOR_PATH, 'wb') as f:
        pickle.dump(user_following_vector_model, f)


def calculate_user_bio_vector_batch():
    global user_bio_vector_model
    user_bio_vector_model = {
        "index2word": [],
        "word2index": {},
    }
    user_bio_vector = []
    users = User.objects.all()
    texts = [" ".join(get_content_words(json.loads(user.bio))) for user in users]
    tfidf = TfidfVectorizer().fit(texts)

    user_bio_vector_model["tfidf"] = tfidf

    for i, user in enumerate(users):
        key = user.user_name + "@" + user.instance

        vec = calculate_user_bio_vector(user)
        user_bio_vector.append(vec)

        user_bio_vector_model["index2word"].append(key)
        user_bio_vector_model["word2index"][key] = i

    user_bio_vector_model["syn0norm"] = np.array(user_bio_vector)

    with open(settings.USERBIOVECTOR_PATH, 'wb') as f:
        pickle.dump(user_bio_vector_model, f)
