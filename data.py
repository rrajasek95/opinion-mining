import pandas as pd
from nltk.tokenize import word_tokenize

def get_annotated_examples_with_opinions():
    df = pd.read_csv('processed_data/annotated_lexicon_based_reviews.csv', dtype={
        'opinion_target_pairs': 'string'
    })
    texts = df['text'].tolist()
    opinions = df['opinion_target_pairs'].tolist()
    return list(zip(texts, opinions))

def get_annotated_examples_all():
    df = pd.read_csv('processed_data/annotated_lexicon_based_reviews.csv')
    reviews = df['text'].tolist()
    return reviews

def all_lexicon_based_reviews():
    df = pd.read_csv('processed_data/lexicon_based_reviews.csv')
    reviews = df['text'].tolist()
    filtered_reviews = [review for review in reviews if len(word_tokenize(review)) < 500]
    # rev_lens = []
    # for review in reviews:
    #     rev_lens.append(len(word_tokenize(review)))
    # print(describe(rev_lens))
    return reviews