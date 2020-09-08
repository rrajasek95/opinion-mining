from collections import defaultdict
import spacy
from spacy.tokens import Token

import re
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
        self._configure_tokenizer()

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

        self.simple_association_pattern = re.compile(
            "(pizza|lasagna|bruschetta|gelato|gnocchi) (is|was) (\w+)")
        

    def _configure_tokenizer(self):
        def is_pronominal(token):
            return token.text.lower() in ("it", "they")
        
        def is_singular_item(token):
            return token.text.lower() == "it" and token.pos_ == "PRON"

        def is_plural_item(token):
            return token.text.lower() == "they"

        def is_quantifier(token):
            return token.text.lower() in ("every")
        
        def is_anaphora(token):
            return token._.is_pronominal or token._.is_quantifier

        def is_resolved_pronoun(token):
            return token._.in_coref and token.pos_ == "PRON"

        Token.set_extension("is_pronominal", getter=is_pronominal)
        Token.set_extension("is_resolved_pronoun", getter=is_resolved_pronoun)
        Token.set_extension("is_quantifier", getter=is_quantifier)
        Token.set_extension("is_anaphora", getter=is_anaphora)
        Token.set_extension("is_singular_item", getter=is_singular_item)

    def _process_matched_aspect_label(self, token):
        text = token.text.lower()
        return self.plural_aspects.get(text, text)

    def _extract_spacy_features(self, text):
        return self.nlp(text)

    def _is_direct_keyword(self, token):
        return token.text.lower() in self.aspect_lexicon

    def _parse_review(self, doc):
        dprint(doc._.coref_clusters)
        aspect_opinions = defaultdict(list)

        previous_sentence_mentions = []
        current_sentence_mentions = []

        for token in doc:
            if token.is_sent_start:
                previous_sentence_mentions = current_sentence_mentions
                current_sentence_mentions = []
            
            dprint(token.text, token.pos_, token.dep_, token.head.text, token.head.pos_, [child.text for child in token.children])
            
            if self._is_direct_keyword(token):
                parses = self.parser.parse_zhuang_phrases(token)

                aspect_label = self._process_matched_aspect_label(token)
                current_sentence_mentions.append(aspect_label)
                if parses:
                    aspect_opinions[aspect_label] += parses
            elif token._.is_anaphora:
                if token._.is_singular_item:
                    print(token.text)
                    
                    if len(current_sentence_mentions) > 0:
                        matched_aspect = current_sentence_mentions[-1] 
                    elif len(previous_sentence_mentions) > 0:
                        matched_aspect = previous_sentence_mentions[-1]
                    else:
                        # This may be a dummy pronoun
                        continue
                    dprint(matched_aspect)
                    parses = self.parser.parse_zhuang_phrases(token)
                    if parses:
                        dprint(matched_aspect)
                        aspect_opinions[matched_aspect] += parses
        
        for g in re.finditer(self.simple_association_pattern, doc.text):
            sentiment = g.group(1, 3)
            item_opinions = aspect_opinions[sentiment[0]]
            for opinion in item_opinions:
                if sentiment[1] in opinion: 
                    # Check if we have a more complete parse using our earlier rules
                    break
            else:
                item_opinions.append(sentiment[1])

        dprint("\n")
        return aspect_opinions

    def extract_descriptions(self, raw_reviews):

        reviews = []
        
        docs = self.nlp.pipe(raw_reviews, disable=["ner"])

        for doc in tqdm(docs):
            reviews.append(self._parse_review(doc))
        
        return reviews