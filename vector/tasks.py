import pickle
import gensim

from django.conf import settings


def calculate_word_vector(file_name):
    corpus = gensim.models.word2vec.Text8Corpus(file_name)
    model = gensim.models.Word2Vec(corpus, size=300, window=5, min_count=5, sample=1e-3, sg=1, hs=1, negative=5)
    with open(settings.WORDVECTOR_PATH, 'wb') as f:
        pickle.dump(model, f)
