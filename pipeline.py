from collections import defaultdict
import spacy
import neuralcoref

from tqdm.auto import tqdm

import logging
from concurrent.futures.thread import ThreadPoolExecutor

DEBUG = True
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args,*kwargs)

class Parser():
    def __init__(self):
        super().__init__()

    def parse_zhuang_phrases(self, token):
        """
        Zhuang defines the following templates for movies,
        that are very well satisfiable for food:
        1. NN-amod-JJ (NOUN-amod-ADJ)
        2. NN-nsubj-JJ (NOUN-nsubj-ADJ)


        head - amod - child (horrible pizza)
        head - nsubj - child

        We define the additional sub cases for the parse:
        1. NN <-amod-JJ(-conj-> JJ) adjectives defined as conjuncts (cold & hard)
        2. NN <-nsubj- VB -acomp/attr-> JJ (NOUN <-nsubj - VB -acomp->JJ)
        3. NN <-nsubj- JJ -advmod-> ADV (the pizza is very good)
        4. 
        """
        parses = []
        for child in token.children:
            if child.dep_ == "amod" and child.pos_ == "ADJ":
                modified_phrase = []
                for subchild in child.children:
                    if subchild.dep_ == "npadvmod":
                        modified_phrase.append(subchild.text)
                modified_phrase.append(child.text)
                parses.append(" ".join(modified_phrase))

                # Sub case 1: conjuct adjectives
                for subchild in child.children:
                    if subchild.dep_ == "conj" and subchild.pos_ == "ADJ":
                        parses.append(subchild.text)
                
            elif child.dep_ == "amod" and child.pos_ == "VERB":
                # Sub case 4
                modified_phrase = []
                for subchild in child.children:
                    if subchild.dep_ == "advmod":
                        modified_phrase.append(subchild.text)
                modified_phrase.append(child.text)
                parses.append(" ".join(modified_phrase))
            elif child.dep_ == "nsubj" and child.pos_ == "ADJ":
                parses.append(child.text)


        if token.dep_ == "nsubj":
            for headchild in token.head.children:
                if headchild.dep_ in ["acomp", "attr"] and headchild.pos_ == "ADJ":
                    modified_phrase = []
                    for headgrandchild in headchild.children:
                        if headgrandchild.dep_ == "advmod":
                            modified_phrase.append(headgrandchild.text)
                    modified_phrase.append(headchild.text)
                    parses.append(" ".join(modified_phrase))
                

        return parses

class Pipeline():
    def __init__(self):
        super().__init__()
        self.nlp = spacy.load('en_core_web_lg')
        neuralcoref.add_to_pipe(self.nlp)

        # We treat entities and aspects to be the same
        self.aspect_lexicon = {
            'bruschetta',
            'pizza',
            'pizzas',
            'lasagna',
            'gnocchi',
            'gelato',
            'gelatos'
        }

        self.plural_aspects = {
            'pizzas': 'pizza',
            'gelatos': 'gelato'
        }

        self.parser = Parser()

    def _process_matched_aspect_label(self, token):
        text = token.text.lower()
        return self.plural_aspects.get(text, text)

    def _extract_spacy_features(self, text):
        return self.nlp(text)

    def _is_direct_keyword(self, token):
        return token.text.lower() in self.aspect_lexicon

    def _is_anaphora(self, token):
        return token._.in_coref and token.pos_ == "PRON"

    def _parse_review(self, doc):
        dprint(doc._.coref_clusters)
        aspect_opinions = defaultdict(list)
        for token in doc:
            dprint(token.text, token.pos_, token.dep_, token.head.text, token.head.pos_, [child.text for child in token.children])
            
            if self._is_direct_keyword(token):
                parses = self.parser.parse_zhuang_phrases(token)

                aspect_label = self._process_matched_aspect_label(token)
                if parses:
                    aspect_opinions[aspect_label] += parses
                
            elif self._is_anaphora(token):
                for cluster in token._.coref_clusters:
                    aspect_count = 0
                    # For any anaphora, match against the head
                    for main_token in cluster.main:
                    
                        matched_aspect = None
                        if main_token.text.lower() in self.aspect_lexicon:
                            
                            aspect_count += 1
                            matched_aspect = self._process_matched_aspect_label(main_token)
                            dprint(matched_aspect)

                        
                    if aspect_count == 1:
                        parses = self.parser.parse_zhuang_phrases(token)

                        if parses:
                            dprint(matched_aspect)
                            aspect_opinions[matched_aspect] += parses
        dprint("\n")
        return aspect_opinions

    def extract_descriptions(self, raw_reviews):

        reviews = []
        
        docs = self.nlp.pipe(raw_reviews, disable=["ner"])

        for doc in tqdm(docs):
            reviews.append(self._parse_review(doc))
        
        return reviews