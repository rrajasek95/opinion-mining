import os
import json

import sys
from pprint import pprint


PROCESSED_DATA_PATH = "processed_data"

def load_business_data():
    with open(os.path.join(
        'Yelp',
        'yelp_academic_dataset_business.json'
    ), 'r') as business_data_file:
        lines = [line.strip() for line in business_data_file]
    
    return lines

def load_restaurants_data():
    with open(os.path.join(
        PROCESSED_DATA_PATH,
        "restaurant_businesses.json"), 'r') as restaurant_file:
        
        lines = [line.strip() for line in restaurant_file]
        return lines

class Dataset(object):
    def __init__(self, business_data):
        super().__init__()
        self.data = business_data

        self.target_path = PROCESSED_DATA_PATH

    def prepare_category_information(self):

        categoriesSet = set()

        for line in self.data:
            data_dict = json.loads(line)
            categories_str = data_dict['categories']
            categories = categories_str.split(", ") if categories_str else []
            categoriesSet.update(categories)

        categoryTerms = sorted(list(categoriesSet))

        with open(os.path.join(
            self.target_path,
            'categories.txt'), 'w') as categoriesFile:
            categoriesFile.writelines([term + '\n' for term in categoryTerms])

        

    def prepare_italian_restaurant_business(self):
        

    
    def prepare_restaurant_businesses(self):
        restaurant_businesses = []
        for line in self.data:
            data_dict = json.loads(line)
            categories_str = data_dict['categories']
            categories = categories_str.split(" ") if categories_str else []

            if "Restaurants" in categories:
                restaurant_businesses.append(line + "\n")
        
        with open(os.path.join(self.target_path, 'restaurant_businesses.json'), 'w') as restaurant_file:
            restaurant_file.writelines(restaurant_businesses)

                

if __name__ == "__main__":
    dataset = Dataset(load_business_data())

    # dataset.prepare_category_information()
    dataset.prepare_restaurant_businesses()