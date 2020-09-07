from pipeline import Pipeline
from pprint import pprint

import pandas as pd

from nltk.tokenize import word_tokenize
from scipy.stats import describe

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

def cherry_picked_examples():
    return [
        # "We visited Pittsburgh last week for my 31st Birthday and booked Dish Osteria as our dinner spot. The restaurant is very cozy. Seating is limited, so I would suggest a reservation. The dinner menu changes daily, but overall, expect scrumptious seafood, pasta, and salad. First of all, the bread is delicious and fresh. We enjoyed snacking on it before receiving our antipasta  and salad. We ordered the Insalata Mista della Casa; the salad was the perfect blend of peppery and crisp greens. I would highly recommend ordering it. Both of the antipastas we requested were the standouts of our meal. The Carpaccio di Manzo literally melted in your mouth. The beef was incredibly fresh and sliced to perfection, and the Reggiano was a nice touch. The cozze was the best bowl of mussels either of us have ever devoured  (and I make mussels regularly at home). The taste was somehow delicate and full of flavor simultaneously. I can not imagine a better way to start off your dinner than with these two dishes. By the time we ate our main courses, we were already drunk on the flavors Dish Osteria has to offer. I ordered the Spaghetti ai Frutti di Mare. All of the shellfish was fresh and cooked to perfection. The spaghetti was a firm al dente, which is exactly how I prefer it. Amazing dish. My husband ordered the Saltimbocca di Vitello. The meat was delicious, but somehow the least impressive part of the plate. The butter potato gnocchi was seriously Heavenly! The texture was like fluffy marshmallow, and the flavor - buttery goodness. If I could eat it every day, I would. The brussel's sprouts were sauteed well and incredibly flavorful. Overall, our dinner was an incredibly experience, and if we lived in Pittsburgh, Dish is a place we would dine at regularly. We will remember our dining experience at Dish Osteria for years to come. It was simply delicious, and the best restaurant we visited while in Pittsburgh."
        # "I've had bad experiences at other Pizza Hut shops, but this one always gives me well made pizzas. Pizza is always fresh, never burnt, always done by the time I get there. There's always people in there so I'm assuming they feel the same way. Try the stuffed crust and crust toppers."
        # "We found this place from the awesome Yelp! Reviews. It did not disappoint!! From my husband's fried mozzarella to my gluten free spinach artichoke dip, then on to the fabulous gluten free pizza, we left stuffed. We were celebrating our honeymoon in the area and through conversation they found out and gave us an appetizer on the house! If we lived here this would be a go to spot for us! Thank you NYPD! You made us feel so special and full!"
        # 'One of my favorite restaurants in the world. I’ve been there over a dozen times and this time I decided to have the pizza and the lasagna. The pizza was incredible while the lasagna was undercooked. When I went there last, I had the gnocchi and it was mindnumbingly good.',
        """
        In the heart of Chinatown, I discovered it enroute to Kensington Market one day. It's quite hard to see, if you don't know it's there. First experience was very positive - would definitely return!

ATMOSPHERE: Small space. Think Banh Mi Boys, and other trendy over-the-counter eateries. Vibe is casual. Free WiFi is nice.

SERVICE: Okay. Staff does their job, but not overly helpful upon entering the space. Maybe because it's an over-the-counter style place, but it would have been nice to be walked through their ordering process and menu.

PRICE: Average. Depends on the size of pizza you order.The small pizza ($7-9.50) is filling for one. Large size pizza ($13-18.50) is good for sharing... or one VERY hungry person.  Pasta portions are very generous for the price tag ($9-14)


FOOD: My friends and I were here for the first time, and we thought it was a pizza place so we all ordered pizza. It wasn't until we were waiting for the food to come, that we looked around and realised EVERY other table around us only had pasta on them. Guess we gotta come back to try! We did notice that the menu said their pasta is homemade. So will definitely come back.

Here's the pizza we ordered:

Peking Duck Pizza - Very tasty! Rich flavours that work well. But it's heavy, so come hungry - or order to share.

Margherita - Good, but not the best. I recommend trying the more "special" toppings instead.

Shall return, and/or try other locations.
        """
    ]

if __name__ == "__main__":
    
    

    pipeline = Pipeline()

    # pprint(list(enumerate(pipeline.extract_descriptions(get_annotated_examples_all()))))
    # pprint(list(enumerate(pipeline.extract_descriptions(all_lexicon_based_reviews()))))
    pprint(list(enumerate(pipeline.extract_descriptions(cherry_picked_examples()))))
    # pprint(list([(i + 1, e) for (i, e) in enumerate(
    #     pipeline.extract_descriptions(get_provided_examples()))]))