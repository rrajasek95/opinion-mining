from pipeline import Pipeline
from pprint import pprint
from scipy.stats import describe

from data import get_annotated_examples_all, all_lexicon_based_reviews

def get_provided_examples():
    return [
        'One of my favorite restaurants in the world. I’ve been there over a dozen times and this time I decided to have the pizza and the lasagna. The pizza was incredible while the lasagna was undercooked. When I went there last, I had the gnocchi and it was mindnumbingly good.',
        'Pizza and gelato were both great.',
        'Never go here. Cold bruschetta and undercooked lasagna.',
        'Too expensive for the taste. Service and gelato were both incredible.',
        'El Tutti Fruti needs more options on their menu.',
        'OMFG that horrible lasagna.',
        'My jaws still hurt from eating the cold & hard bruschetta.',
        'I can still taste the spicy tomato sauce on that pizza. It was delicious.',
        'I had the pizza, lasagna and gelato. The first two were ok and the gelato was great.'
    ]

def cherry_picked_examples():
    return [
        """
        "Delicious pizza! I had the Lambretta special pizza, minus the prosciutto because I was in the mood for vegetarian (I'm sure it's delicious with the prosciutto too though). It was HUGE but it was thin crust and it was all I was having and I was hungry so I ate the whole thing myself!

The service was very fast and friendly, and the atmosphere and decor of the restaurant were very pleasant and modern. 

I will definitely come back here! The pizza was made from high quality, authentic ingredients, and I didn't feel stuffed in a bad way like I do at other pizza places. I felt great afterwards."
        """
    ]

if __name__ == "__main__":
    
    

    pipeline = Pipeline()

    # pprint(list(enumerate(pipeline.extract_descriptions(get_annotated_examples_all()))))
    # pprint(list(enumerate(pipeline.extract_descriptions(all_lexicon_based_reviews()))))
    # pprint(list(enumerate(pipeline.extract_descriptions(cherry_picked_examples()))))
    pprint(list([(i + 1, e) for (i, e) in enumerate(
        pipeline.extract_descriptions(get_provided_examples()))]))