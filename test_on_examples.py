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
I used to like the pizza from here. Last time I ordered it was still doughy and I had to cook longer. Today it was ice cold. Not even lukewarm. My kid was screaming for pizza so I didn't send it back. But, I won't ever order from here again. $31 plus tip for a cold pizza and cold soup. There was a piece of "garlic bred". It was half a sub roll uncooked with some garlic butter on it. Yum. Should have had a can of Progresso and a frozen pizza and saved $25. Wait, I could have saved $35. I tipped $10. I figure a poor kid driving his own car deserves a decent tip. I called to let them know and she said sorry we can replace the pizza. My kid ate the cold thing anyway. And who wants to wait another hour for the replacement? Blah. Next time I'll drive my lazy self over to Bonnanos and pick up a pizza myself.
        """
    ]

if __name__ == "__main__":
    
    

    pipeline = Pipeline()

    # pprint(list(enumerate(pipeline.extract_descriptions(get_annotated_examples_all()))))
    # pprint(list(enumerate(pipeline.extract_descriptions(all_lexicon_based_reviews()))))
    # pprint(list(enumerate(pipeline.extract_descriptions(cherry_picked_examples()))))
    
    # pprint(list([(i + 1, e) for (i, e) in enumerate(
    #     pipeline.extract_descriptions(get_provided_examples()))]))
    provided_examples = cherry_picked_examples()
    res = zip(provided_examples, pipeline.extract_descriptions(provided_examples))

    for i, r in enumerate(res):
        # print(f"{i + 1} {r[0]} {r[1]}")
        print(f"Review ID: {i + 1}")
        print(f"Text: {r[0]}")
        print(f"Output: {r[1]}")
        print()