from pipeline import Pipeline
from pprint import pprint

if __name__ == "__main__":
    
    examples = [
        'One of my favorite restaurants in the world. I’ve been there over a dozen times and this time I decided to have the pizza and the lasagna. The pizza was incredible while the lasagna was undercooked. When I went there last, I had the gnocchi and it was mindnumbingly good.',
        'Pizza and gelato were both great.',
        'Never go here. Cold bruschetta and undercooked lasagna.',
        'Too expensive for the taste. Service and gelato were both incredible.'
        'El Tutti Fruti needs more options on their menu.',
        'OMFG that horrible lasagna.',
        'My jaws still hurt from eating the cold & hard bruschetta.',
        'I can still taste the spicy tomato sauce on that pizza. It was delicious.',
        'I had the pizza, lasagna and gelato. The first two were ok and the gelato was great.'
    ]

    pipeline = Pipeline()

    pprint(pipeline.extract_descriptions(examples))