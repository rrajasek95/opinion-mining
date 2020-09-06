from collections import defaultdict
import spacy
import neuralcoref



class Pipeline():
    def __init__(self):
        super().__init__()
        self.nlp = spacy.load('en_core_web_lg')
        neuralcoref.add_to_pipe(self.nlp)

        # We treat entities and aspects to be the same
        self.aspect_lexicon = {
            'bruschetta',
            'pizza',
            'lasagna',
            'gnocchi',
            'gelato'
        }
    
    def _parse_zhuang_phrases(self, token):
        """
        Zhuang defines the following templates for movies,
        that are very well satisfiable for food:
        1. NN-amod-JJ (NOUN-amod-ADJ)
        2. NN-nsubj-JJ (NOUN-nsubj-ADJ)


        head - amod - child (horrible pizza)
        head - nsubj - child

        We define the additional sub cases for the parse:
        1. NN-amod-JJ(-conj-JJ) adjectives defined as conjuncts (cold & hard)
        2. NN <-nsubj- VB -acomp-> JJ (NOUN <-nsubj - VB -acomp->JJ)
        """
        parses = []
        for child in token.children:
            if child.dep_ == "amod" and child.pos_ == "ADJ":
                parses.append(child.text)

                # Sub case 1: conjuct adjectives
                for subchild in child.children:
                    if subchild.dep_ == "conj" and subchild.pos_ == "ADJ":
                        parses.append(subchild.text)

            elif child.dep_ == "nsubj" and child.pos_ == "ADJ":
                parses.append(child.text)


        if token.dep_ == "nsubj":
            print(list(token.head.children))
            for headchild in token.head.children:
                if headchild.dep_ == "acomp" and headchild.pos_ == "ADJ":
                    parses.append(headchild.text)
                elif headchild.dep_ == "advc" and headchild.pos_ == "ADJ":
                    parses.append(headchild.text)

            

        return parses

    def _extract_spacy_features(self, text):
        return self.nlp(text)

    def _is_direct_keyword(self, token):
        return token.text.lower() in self.aspect_lexicon

    def _is_anaphora(self, token):
        return token._.in_coref and token.pos_ == "PRON"

    def _parse_review(self, review):
        doc = self._extract_spacy_features(review)
        print(doc._.coref_clusters)
        aspect_opinions = defaultdict(list)
        for token in doc:
            print(token.text, token.pos_, token.dep_, token.head.text, token.head.pos_, [child.text for child in token.children])
            
            if self._is_direct_keyword(token):
                parses = self._parse_zhuang_phrases(token)

                if parses:
                    aspect_opinions[token.text.lower()] += parses
            
            elif self._is_anaphora(token):
                for cluster in token._.coref_clusters:
                    aspect_count = 0
                    # For any anaphora, match against the head
                    for main_token in cluster.main:
                    
                        matched_aspect = None
                        if main_token.text.lower() in self.aspect_lexicon:
                            
                            aspect_count += 1
                            matched_aspect = main_token
                        
                    if aspect_count == 1:

                        parses = self._parse_zhuang_phrases(token)

                        if parses:
                            aspect_opinions[matched_aspect.text.lower()] += parses

        print()
        return aspect_opinions

    def extract_descriptions(self, raw_reviews):

        reviews = []
        for raw_review in raw_reviews:
            reviews.append(self._parse_review(raw_review))
        
        return reviews