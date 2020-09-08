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

    def _extract_direct_dependence(self, token):
        parses = []
        for headchild in token.head.children:
            if headchild.dep_ in ["acomp", "attr"] and headchild.pos_ == "ADJ":
                modified_phrase = []
                for headgrandchild in headchild.children:
                    if headgrandchild.dep_ == "advmod":
                        modified_phrase.append(headgrandchild.text)
                modified_phrase.append(headchild.text)
                parses.append(" ".join(modified_phrase))
        
        return parses

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
        4. NN <-nsubj- JJ -advmod-> ADV (-advmod-> ADV )* (the pizza is very good and delicious)
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
            # Token is a noun subject, so we can find adjective clasuses
            parses = self._extract_direct_dependence(token)
        elif token.dep_ == "conj":
            # The token has a conjuct dependency, to another token (of potentially equal rank)
            # find the opinion of its head token
            parses = self._extract_direct_dependence(token.head)

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
            'gelatos': 'gelato',
            'bruschettas': 'bruschetta',
            'lasagne': 'lasagna'
        }

        self.parser = Parser()

        self.simple_association_pattern = re.compile(
            "(pizza|lasagna|bruschetta|gelato|gnocchi) (is|was) (\w{3,})")
        self.simple_association_pattern_plural = re.compile(
            "(pizzas|lasagne|bruschettas|gelatos|gnocchi) (are,were) (\w{3,})"
        )

        # Only doing from 1 to 5 for now since there are only 5 items
        # Possible extension is to chunk numbers together
        self.word_to_number = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
        }

    def _numericalize_value(self, token):
        return self.word_to_number.get(token.text.lower())

    def _configure_tokenizer(self):
        def is_pronominal(token):
            return token.text.lower() in ("it", "they")
        
        def is_singular_item(token):
            return token.text.lower() == "it" and token.pos_ == "PRON"

        def is_plural_item(token):
            return token.text.lower() == "they"

        def is_quantifier(token):
            return token.text.lower() in ("every", "everything")
        
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

    def _parse_anaphora(self, token, mentions, mention_rank, aspect_opinions):
        if token._.is_singular_item:
            dprint(token.text)
            
            has_neighboring_mentions = len(mentions) > 0 and mentions[-1][0] - mention_rank < 2

            if has_neighboring_mentions: # Avoid overly distant matching
                matched_aspect = mentions[-1][1]

                dprint(matched_aspect)
                parses = self.parser.parse_zhuang_phrases(token)
                if parses:
                    dprint(matched_aspect)
                    aspect_opinions[matched_aspect] += parses
            # The other alternative are dummy pronouns
        elif token._.is_quantifier:
            matched_mentions = []
            has_neighboring_mentions = len(mentions) > 0 and mentions[-1][0] - mention_rank < 2
            if has_neighboring_mentions:
                # Collection all mentions of equal rank in the backwards direction
                # ensures we don't capture unnecessary mentions
                matched_mentions.append(mentions[-1])

                for i in range(len(mentions) - 2, -1, -1):
                    if mentions[i][0] != matched_mentions[-1][0]:
                        break
                    matched_mentions.append(mentions[i])
                dprint(matched_mentions)
                parses = self.parser.parse_zhuang_phrases(token)
                if parses:
                    matched_aspects = [mention[1] for mention in matched_mentions]
                    for matched_aspect in matched_aspects:
                        aspect_opinions[matched_aspect] += parses


    def _parse_review(self, doc):
        dprint(doc._.coref_clusters)
        aspect_opinions = defaultdict(list)

        mentions = []

        # Using rank to group mentions
        mention_rank = 0
        for token in doc:
            if token.is_sent_start and token.text not in ["("]:
                mention_rank += 1
            
            dprint(token.text, token.pos_, token.dep_, token.head.text, token.head.pos_, [child.text for child in token.children])
            
            if self._is_direct_keyword(token):
                parses = self.parser.parse_zhuang_phrases(token)

                aspect_label = self._process_matched_aspect_label(token)
                mentions.append((mention_rank, aspect_label))
                if parses:
                    aspect_opinions[aspect_label] += parses
            elif token._.is_anaphora:
                self._parse_anaphora(token, mentions, mention_rank, aspect_opinions)
            elif token.pos_ == "NUM" and token.dep_ == "nsubj":

                if re.match("\d+", token.text) or len(mentions) < 1 or mentions[-1][0] < 2:
                    # Ignore actual numbers
                    continue
                matched_mentions = []
                # This is for now a special case not associated with the parser
                # until i can find a better way to implement this
                dprint("number case")
                take_from = "tail"
                for child in token.children:
                    if child.text == "first":
                        take_from == "head"

                matched_mentions.append(mentions[-1])

                for i in range(len(mentions) - 2, -1, -1):
                    if mentions[i][0] != matched_mentions[-1][0]:
                        break
                    matched_mentions.append(mentions[i])
                numericalized_val = self._numericalize_value(token)

                if take_from == "tail":
                    matched_mentions = matched_mentions[-min(numericalized_val, len(matched_mentions)):]
                else:
                    matched_mentions = matched_mentions[:min(numericalized_val, len(matched_mentions))]

                parses = self.parser.parse_zhuang_phrases(token)
                if parses:
                    matched_aspects = [mention[1] for mention in matched_mentions]
                    for matched_aspect in matched_aspects:
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