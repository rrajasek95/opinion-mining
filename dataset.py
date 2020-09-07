import os
import json

import sys
from pprint import pprint
from tqdm.auto import tqdm

import pandas as pd
from collections import defaultdict

PROCESSED_DATA_PATH = "processed_data"

def load_processed_data(path):
    with open(os.path.join(
        PROCESSED_DATA_PATH,
        path), 'r') as restaurant_file:
        
        lines = [line.strip() for line in restaurant_file]
    return lines

def load_yelp_academic(path):
    with open(os.path.join(
        'Yelp',
        path
    ), 'r') as academic_data_file:
        lines = [line.strip() for line in tqdm(academic_data_file)]
    
    return lines

def load_business_data():
    return load_yelp_academic("yelp_academic_dataset_business.json")

def load_restaurants_data():
    return load_processed_data("restaurant_businesses.json")

def load_italian_restaurants_data():
    return load_processed_data("italian_restaurant_businesses.json")

class Dataset(object):
    def __init__(self):
        super().__init__()

        self.target_path = PROCESSED_DATA_PATH

    def _save_processed_data(self, filename, data):
        with open(os.path.join(self.target_path, filename), 'w') as processed_data_file:
            processed_data_file.writelines(data)

    def prepare_category_information(self):
        categoriesSet = set()
        for line in load_business_data():
            data_dict = json.loads(line)
            categories_str = data_dict['categories']
            categories = categories_str.split(", ") if categories_str else []
            categoriesSet.update(categories)

        categoryTerms = sorted(list(categoriesSet))

        self._save_processed_data('categories.txt', [term + '\n' for term in categoryTerms])
    

    def prepare_italian_restaurant_business(self):
        businesses = []
        
        for line in load_restaurants_data():
            data_dict = json.loads(line)
            categories_str = data_dict['categories']
            categories = categories_str.split(", ") if categories_str else []

            if "Italian" in categories:
                businesses.append(line + "\n")

        self._save_processed_data('italian_restaurant_businesses.json', businesses)

    
    def prepare_restaurant_businesses(self):
        restaurant_businesses = []
        for line in load_business_data():
            data_dict = json.loads(line)
            categories_str = data_dict['categories']
            categories = categories_str.split(" ") if categories_str else []

            if "Restaurants" in categories:
                restaurant_businesses.append(line + "\n")

        self._save_processed_data('restaurant_businesses.json', restaurant_businesses)

    def italian_restaurant_reviews(self):
        italian_restaurant_info = {}
        
        for line in load_italian_restaurants_data():
            data_dict = json.loads(line)
            italian_restaurant_info[data_dict["business_id"]] = data_dict
        
        italian_reviews = []

        # Doing file open since the reviews data is huge, more memory efficient
        with open(os.path.join(
            'Yelp',
            'yelp_academic_dataset_review.json'
        ), 'r') as academic_data_file:
            for line in tqdm(academic_data_file):
                data_dict = json.loads(line.strip())
                review_business = data_dict['business_id']

                if review_business in italian_restaurant_info:
                    italian_reviews.append(line)
        
        self._save_processed_data('italian_restaurant_reviews.json', italian_reviews)

    def most_popular_italian_restaurants(self):
        italian_restaurant_info = {}

        for line in load_italian_restaurants_data():
            data_dict = json.loads(line)
            data_dict["num_reviews"] = 0
            italian_restaurant_info[data_dict["business_id"]] = data_dict

        for line in load_processed_data("italian_restaurant_reviews.json"):
            data_dict = json.loads(line)
            review_business = data_dict['business_id']
            business = italian_restaurant_info[review_business]
            business["num_reviews"] += 1
        
        
        sorted_businesses = sorted(list(italian_restaurant_info.values()), key=lambda x: -x['num_reviews'])
        sorted_businesses_lines = [json.dumps(biz) + "\n" for biz in sorted_businesses]
        self._save_processed_data('italian_restaurants_sorted_by_reviews.json', sorted_businesses_lines)

    def restaurant_reviews_containing_lexicon_items(self):
        lexicon = [
            'pizza',
            'gnocchi',
            'gelato',
            'lasagna',
            'bruschetta',
        ]

        reviews = []
        reviews_dicts = []
        num_mentioned_items = defaultdict(int)
        for line in load_processed_data("italian_restaurant_reviews.json"):
            data_dict = json.loads(line)
            lower_text = data_dict['text'].lower()
            for item in lexicon:
                if item in lower_text:
                    reviews.append(line)
                    reviews_dicts.append(data_dict)
                    num_mentioned_items[item] += 1
        print(num_mentioned_items)
        print(reviews[0])
        self._save_processed_data('lexicon_item_reviews.json', reviews)
        reviews_df = self._prepare_dataframe_from_data('lexicon_based_reviews.csv', reviews_dicts, columns=['review_id', 'text'])

        reviews_df.iloc[:100].to_csv('lexicon_based_reviews_sample.csv', columns=['review_id', 'text'], index_label='review_id')


    def _prepare_dataframe_from_data(self, filename, data, columns):
        file_path = os.path.join(self.target_path, filename)
        df = pd.DataFrame(data)
        df.to_csv(file_path, columns=columns, index_label='review_id')

        return df
    
if __name__ == "__main__":
    dataset = Dataset()
    dataset.restaurant_reviews_containing_lexicon_items()